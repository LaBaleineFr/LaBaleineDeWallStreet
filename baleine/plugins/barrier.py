import asyncio
from baleine import command, conf, embed, exception, util
import discord, logging, random, yaml

logger = logging.getLogger(__name__)

# ============================================================================

class NoQuizz(Exception):
    """ Requested quizz does not exist """
    pass

class AFKError(Exception):
    """ User went AFK during the quizz """
    pass

# ============================================================================

class BarrierManager(object):
    """ Simple object that holds pre-loaded quizzes """

    def __init__(self):
        self.cache = {}

    def quizz(self, name):
        """ Return quizz definition for given name, with caching """
        name = name.lower()
        try:
            result = self.cache[name]
        except KeyError:
            try:
                result = self.load_quizz(name)
            except NoQuizz:
                self.cache[name] = None
                raise
            except Exception as exc:
                logger.exception('error trying to load quizz %s' % name)
                raise NoQuizz('Je ne connais pas le quizz "%s".' % name)
            self.cache[name] = result

        if result is None:
            raise NoQuizz('Je ne connais pas le quizz "%s".' % name)
        return result

    def load_quizz(self, name):
        """ Load quizz with specified name """
        for qconf in conf.settings.barrier['quizzes']:
            if qconf.get('name').lower() == name:
                break
        else:
            raise NoQuizz('Je ne connais pas le quizz "%s".' % name)

        with open(qconf['file'], 'rb') as fd:
            data = yaml.load(fd)

        data.update(qconf)
        return data

manager = BarrierManager()  # singleton

# ============================================================================

class Barrier(command.Command):
    """ Bot command that runs quizzes """
    name = 'barrier'
    default_timeout = 600   # in seconds

    errors = {
        'needs_server': 'Commande utilisable depuis un serveur uniquement.',
        'usage': 'Quel quizz voulez-vous ?',
        'busy': 'Je suis déjà en train de vous parler.',
        'dm_permission_denied': 'Je dois pouvoir vous envoyer un DM. '
                                'Merci d\'autoriser les messages privés des '
                                'membres du serveur.',
        'exception': '{}',
    }

    messages = {
        'timeout': 'Délai écoulé.',
        'success': 'Quizz réussi :thumbsup:',
        'failure': 'Quizz raté :thumbsdown:',
        'end': 'Fin du quizz',
        'score_title': 'Score',
        'score_text': 'Vous avez répondu bon à {score} question(s) sur {number}.',
        'question_number': 'Question n°{number}',
        'mcq_choices_title': 'Choix',
        'mcq_invalid': 'Veuillez répondre avec le numéro de votre réponse',
    }

    async def execute(self, message, args):
        # Role attribution will need a server to run on
        if message.server is None:
            await self.error('needs_server')
            return

        if len(args) != 1:
            await self.error('usage')
            return

        # Locate the requested quizz
        try:
            quizz = manager.quizz(args[0])
        except NoQuizz as exc:
            await self.error('exception', exc)
            return

        try:
            # Run the quizz in a chat session
            async with self.client.get_private_chat(message.author) as chat:
                success = await self.run_quizz(chat, quizz)
        except exception.BusyError:
            await self.error('busy')
            return
        except discord.errors.Forbidden:
            await self.error('dm_permission_denied')
            return

        if success:
            role = quizz.get('grant_role', None)
            if role is not None:
                role = util.find_role(message.server, role)
                logger.info('granting role {role.name} to {user.name} [{user.id}]'.format(
                             role=role, user=message.author))
                await self.client.add_roles(message.author, role)

    async def run_quizz(self, chat, quizz):
        """ Run given quizz in the (owned) chat session """

        # If quizz has an introduction text, play it first
        text = quizz.get('introduction')
        if text:
            obj = embed.from_dict(text)
            self.customize_embed(obj, quizz)
            await chat.send('', embed=obj)
            await asyncio.sleep(5)

        # Select a random sample of questions
        questions = quizz['questions']
        to_ask = min(quizz.get('num_questions', len(questions)), len(questions))
        questions = random.sample(questions, to_ask)

        # Ask each question in turn, counting scores
        score, min_score = 0, min(quizz.get('min_score', to_ask), to_ask)
        try:
            for index, question in enumerate(questions, 1):
                if await self.ask_question(chat, quizz, question, index):
                    score += 1
        except AFKError:
            success, message = False, self.messages['timeout']
        else:
            success = score >= min_score
            message = (quizz.get('success', self.messages['success']) if success else
                       quizz.get('failure', self.messages['failure']))

        # Display results
        result = discord.Embed()
        result.title = self.messages['end']
        result.description = message
        self.customize_embed(result, quizz)

        result.add_field(
            name=self.messages['score_title'],
            value=self.messages['score_text'].format(
                score=score,
                minimum=min_score,
                number=len(questions),
            ),
            inline=False,
        )
        await chat.send(result.description, embed=result)
        return success

    def customize_embed(self, obj, quizz):
        """ Add fancy markings to all embeds, if the quizz defines any """
        author = quizz.get('author', None)
        if author is not None:
            embed.EmbedParsers.parse_author(obj, 'author', author)

    async def ask_question(self, chat, quizz, question, index):
        """ Play a single quizz question in the chat, return whether answer was correct """
        mode = question.get('mode', 'mcq')

        # Create a nice embed for the question
        if isinstance(question['question'], str):
            obj = discord.Embed()
            obj.description = question['question']
        else:
            obj = embed.from_dict(question['question'])

        obj.title = self.messages['question_number'].format(number=index)
        self.customize_embed(obj, quizz)

        # Dispatch question to handler for requested mode
        handler = getattr(self, 'ask_%s_question' % mode)

        is_correct, reply = await handler(chat, quizz, question, obj)

        # Show a reaction, if the feature is enabled
        if quizz.get('feedback', False) and reply is not None:
            await self.client.add_reaction(reply, '\U0001F44D' if is_correct else '\U0001F44E')

        return is_correct

    async def ask_mcq_question(self, chat, quizz, question, obj):
        """ Ask a multiple choice question """
        if not isinstance(question['answers'], (list, tuple)):
            raise exception.ConfigurationError('for a mcq question, answers must be a list')

        answers = list(question['answers'])
        correct = answers[0]
        random.shuffle(answers)

        obj.add_field(
            name=self.messages['mcq_choices_title'],
            value='\n'.join(
                '%s. %s' % (index, text)
                for index, text in enumerate(answers, 1)
            ),
            inline=False,
        )

        # Ask question
        await chat.send('', embed=obj)

        while True:
            reply = await chat.wait_reply(timeout=quizz.get('timeout', self.default_timeout))
            if reply is None:
                raise AFKError()
            try:
                value = answers[int(reply.content) - 1]
            except (ValueError, IndexError):
                await chat.send(self.messages['mcq_invalid'])
                continue
            break

        return ((value == correct), reply)

    async def ask_text_question(self, chat, quizz, question, obj):
        """ Ask an open question """
        answers = question['answers']
        answers = [answers] if isinstance(answers, (str, int, float)) else list(answers)

        await chat.send('', embed=obj)
        reply = await chat.wait_reply(timeout=quizz.get('timeout', self.default_timeout))
        if reply is None:
            raise AFKError()

        return (reply.content.lower().strip() in (
                    str(answer).lower().strip() for answer in answers
                ),
                reply)
