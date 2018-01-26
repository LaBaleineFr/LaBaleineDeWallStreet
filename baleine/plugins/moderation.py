import discord, logging
from baleine import command, exchange, util

logger = logging.getLogger(__name__)


class Ban(command.Command):
    """ Bot command that bans a user """
    name = 'ban'

    errors = {
        'usage': '{name} member reason',
        'mention_number': 'la commande doit mentionner exactement un utilisateur.',
        'bot_permission': 'je n\'ai pas les permissions pour bannir {user}.',
        'user_permission': 'vous n\'avez pas les permissions pour bannir {user}.',
    }

    messages = {
        'ban': '{user} a été banni du serveur: *{reason}*',
    }

    async def execute(self, message, args):
        if len(args) < 2:
            await self.error('usage', name=self.name)
            return

        if len(message.mentions) != 1:
            await self.error('mention_number')
            return

        member = message.mentions[0]
        if member.top_role >= message.author.top_role:
            await self.error('user_permission', user=member.display_name)
            return

        reason = ' '.join(args[1:])

        try:
            await member.ban(reason=reason, delete_message_days=0)
        except discord.Forbidden:
            await self.error('bot_permission', user=member.display_name)
        else:
            logger.info('banning {user.display_name} [{user.id}]: {reason}'.format(
                        user=member, reason=reason))
            await self.send(self.messages['ban'].format(user=member.display_name, reason=reason))


#class Clear(command.Command):
    #""" Bot command that deletes messages """
    #name = 'clear'

    #errors = {
        #'invalid_number': 'Je ne comprends pas ce nombre.',
        #'permission_denied': 'Je ne peux pas gérer les messages ici.',
    #}

    #async def execute(self, message, args):
        #if len(args) == 0:
            #await self.clever_clear(message.channel)
            #return

        #if len(args) == 1:
            #try:
                #number = int(args[0])
            #except ValueError:
                #pass
            #else:
                #await self.count_clear(message.channel, number)
                #return

        #await self.search_clear(message.channel, ' '.join(args))

    #async def clever_clear(self, channel):
        #pass
    #async def count_clear(self, channel, number):
        #pass
    #async def search_clear(self, channel, text):
        #pass
