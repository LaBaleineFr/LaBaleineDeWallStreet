import discord
from baleine.exception import PermissionDenied
from baleine.util import find_role, find_channel


class HasRolePermission(object):
    """ Permission that allows commands only for specific roles """

    def __init__(self, guild, roles):
        self.roles = [find_role(guild, role) for role in roles]

    async def check(self, client, message, command):
        for role in self.roles:
            if role in message.author.roles:
                return
        raise PermissionDenied('forbidden')


class ChannelWhitelistPermission(object):
    """ Permission that allows commands only on specific channels """

    def __init__(self, guild, channels):
        self.channels = [find_channel(guild, channel) for channel in channels]

    async def check(self, client, message, command):
        if (isinstance(message.channel, discord.abc.GuildChannel) and
            message.channel not in self.channels):
            raise PermissionDenied('invalid channel')
