import asyncio
from baleine import command, conf, embed, exception, util
import discord, logging, random, yaml

logger = logging.getLogger(__name__)

# ============================================================================

class AFKError(Exception):
    pass

# ============================================================================

class BarrierManager(object):
    def __init__(self):
        self.cache = {}

    def quizz(self, name):
        name = name.lower()
        result = self.cache.get(name)
        if result is None:
            try:
                result = self.load_quizz(name)
            except KeyError:
                logger.exception('Error trying to load quizz %s' % name)
                pass
            except Exception:
                logger.exception('Error trying to load quizz %s' % name)
            self.cache[name] = result
        return result

    def load_quizz(self, name):
        for qconf in conf.settings.barrier['quizzes']:
            if qconf.get('name').lower() == name:
                break
        else:
            raise KeyError('Le quizz %s n\'existe pas.' % name)

        with open(qconf['file'], 'rb') as fd:
            data = yaml.load(fd)

        data.update(qconf)
        return data

manager = BarrierManager()

# ============================================================================

class Barrier(command.Command):
    name = 'barrier'

    async def execute(self, message, args):
        if message.server is None:
            await self.error('Commande utilisable depuis un serveur uniquement.')
            return

        if len(args) != 1:
            await self.error('Quel quizz voulez-vous ?')
            return

        quizz = manager.quizz(args[0])
        if quizz is None:
            await self.error('Je ne connais pas le quizz "%s".' % args[0])
            return

        try:
            async with self.client.get_private_chat(message.author) as chat:
                success = await self.run_quizz(chat, quizz)
        except exception.BusyError:
            await self.error('Je suis déjà en train de vous parler.')
            return

        if success:
            role = quizz.get('grant_role', None)
            if role is not None:
                await self.client.add_roles(chat.user, util.find_role(message.server, role))


    async def run_quizz(self, chat, quizz):
        text = quizz.get('introduction')
        if text:
            obj = embed.from_dict(text)
            self.customize_embed(obj, quizz)
            await chat.send('', embed=obj)

        # Select a random sample of questions
        questions = quizz['questions']
        to_ask = min(quizz.get('num_questions', len(questions)), len(questions))
        questions = random.sample(questions, to_ask)

        score, min_score = 0, min(quizz.get('min_score', to_ask), to_ask)
        try:
            for index, question in enumerate(questions, 1):
                if await self.ask_question(chat, quizz, question, index):
                    score += 1
        except AFKError:
            success, message = False, 'Délai écoulé.'
        else:
            success = score >= min_score
            message = ('Quizz réussi :thumbsup:' if success else
                       'Quizz raté :thumbsdown:')

        # Act upon result
        result = discord.Embed()
        result.title = 'Fin du quizz'
        result.description = message
        self.customize_embed(result, quizz)

        result.add_field(
            name='Score',
            value='Vous avez répondu bon à {score} question(s) sur {number}.'.format(
                score=score,
                minimum=min_score,
                number=len(questions),
            ),
            inline=False,
        )
        await chat.send(result.description, embed=result)
        return success

    def customize_embed(self, obj, quizz):
        author = quizz.get('author', None)
        if author is not None:
            embed.EmbedParsers.parse_author(obj, 'author', quizz['author'])


    async def ask_question(self, chat, quizz, question, index):
        mode = question.get('mode', 'mcq')

        # Create a nice embed for the question
        if isinstance(question['question'], str):
            obj = discord.Embed()
            obj.description = question['question']
        else:
            obj = embed.from_dict(question['question'])

        obj.title = 'Question n°%s' % index
        self.customize_embed(obj, quizz)

        # Add choices if we are in choices mode
        handler = getattr(self, 'ask_%s_question' % mode)
        return await handler(chat, quizz, question, obj)

    async def ask_mcq_question(self, chat, quizz, question, obj):
        answers = list(question['answers'])
        correct = answers[0]
        random.shuffle(answers)

        obj.add_field(
            name='Choix',
            value='\n'.join(
                '%s. %s' % (index, text)
                for index, text in enumerate(answers, 1)
            ),
            inline=False,
        )

        # Ask question
        await chat.send('', embed=obj)

        while True:
            reply = await chat.wait_reply(timeout=60)
            if reply is None:
                raise AFKError()
            try:
                reply = answers[int(reply.content) - 1]
            except (ValueError, IndexError):
                await chat.send('Veuillez répondre avec le numéro de votre réponse')
                continue
            break

        return reply == correct

    async def ask_text_question(self, chat, quizz, question, obj):
        answers = question['answers']
        answers = [answers] if isinstance(answers, (str, int, float)) else list(answers)

        await chat.send('', embed=obj)
        reply = await chat.wait_reply(timeout=60)
        if reply is None:
            raise AFKError()

        return (reply.content.lower().strip() in
                (str(answer).lower().strip() for answer in answers))
