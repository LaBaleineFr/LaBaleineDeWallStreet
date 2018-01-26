import discord
import importlib
import logging
import sys
import traceback
from baleine import private, util
from baleine.command import CommandDispatcher
from baleine.command.loader import load_group
from baleine.exception import ConfigurationError

logger = logging.getLogger(__name__)

def passthrough(name):
    """ Helper function that setups event forwarding to plugins """
    async def caller(self, *args, **kwargs):
        for plugin in self.plugins:
            handler = getattr(plugin, name, None)
            if callable(handler):
                await handler(self, *args, **kwargs)
    return caller


class Bot(discord.Client):
    """ Main bot object, handling connection to discord and receiving events """

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.plugins = self.load_plugins(settings)
        self.private_chats = {}
        self.initialized = False

    def load_plugins(self, settings):
        """ Load plugins from the 'plugins' key in settings dictionary """
        result = []
        for plugin_conf in settings.plugins:
            config = plugin_conf.copy()
            try:
                full_name = config.pop('name')
            except KeyError:
                raise ConfigurationError('Missing plugin name')
            klass = util.import_string(full_name)
            result.append(klass(config))
        return result

    def get_private_chat(self, user):
        """ Obtain a direct communication channel to the user """
        try:
            return self.private_chats[user.id]
        except KeyError:
            chat = private.PrivateChat(self, user)
            self.private_chats[user.id] = chat
            return chat

    async def on_ready(self):
        if self.initialized:
            logger.info('Reconnected as %s [%s]', self.user.name, self.user.id)
            return
        self.initialized = True

        logger.info('Connected as %s [%s]', self.user.name, self.user.id)
        for guild in self.guilds:
            logger.info('    -> on guild %s [%s]', guild.name, guild.id)
            for channel in guild.channels:
                logger.debug('      - channel %s [%s]', channel.name, channel.id)
            for role in guild.roles:
                logger.debug('      - role %s [%s]', role.name, role.id)

            # Load bot command engine, one for each guild we run on
            dispatcher = CommandDispatcher(guild)
            dispatcher.groups = [load_group(guild, command)
                                 for command in self.settings.commands]
            self.plugins.append(dispatcher)

    async def on_error(self, event, *args, **kwargs):
        if self.settings.debug:
            logger.exception('discord error in event: %s' % event)
        else:
            info = sys.exc_info()
            logger.error('%s in %s event: %s', info[0].__name__, event, info[1])

    on_guild_channel_create = passthrough('on_guild_channel_create')
    on_guild_channel_delete = passthrough('on_guild_channel_delete')
    on_guild_channel_update = passthrough('on_guild_channel_update')
    on_guild_channel_pins_update = passthrough('on_guild_channel_pins_update')
    on_group_join = passthrough('on_group_join')
    on_group_remove = passthrough('on_group_remove')
    on_member_join = passthrough('on_member_join')
    on_member_ban = passthrough('on_member_ban')
    on_member_remove = passthrough('on_member_remove')
    on_member_unban = passthrough('on_member_unban')
    on_member_update = passthrough('on_member_update')
    on_message = passthrough('on_message')
    on_message_delete = passthrough('on_message_delete')
    on_message_edit = passthrough('on_message_edit')
    on_private_channel_create = passthrough('on_private_channel_create')
    on_private_channel_delete = passthrough('on_private_channel_delete')
    on_private_channel_update = passthrough('on_private_channel_update')
    on_private_channel_pins_update = passthrough('on_private_channel_pins_update')
    on_reaction_add = passthrough('on_reaction_add')
    on_reaction_clear = passthrough('on_reaction_clear')
    on_reaction_remove = passthrough('on_reaction_remove')
    on_resumed = passthrough('on_resumed')
    on_guild_available = passthrough('on_guild_available')
    on_guild_join = passthrough('on_guild_join')
    on_guild_remove = passthrough('on_guild_remove')
    on_guild_unavailable = passthrough('on_guild_unavailable')
    on_guild_update = passthrough('on_guild_update')
    on_guild_emojis_update = passthrough('on_guild_emojis_update')
    on_guild_role_create = passthrough('on_guild_role_create')
    on_guild_role_delete = passthrough('on_guild_role_delete')
    on_guild_role_update = passthrough('on_guild_role_update')
    on_typing = passthrough('on_typing')
    on_voice_state_update = passthrough('on_voice_state_update')
