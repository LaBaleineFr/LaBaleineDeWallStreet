from baleine.exception import PermissionDenied
from baleine.util import find_role, find_channel


class HasRolePermission(object):
    """ Permission that allows commands only for specific roles """

    def __init__(self, server, roles):
        self.roles = [find_role(server, role) for role in roles]

    async def check(self, client, message, command):
        for role in self.roles:
            if role in message.author.roles:
                return
        raise PermissionDenied('forbidden')


class ChannelWhitelistPermission(object):
    """ Permission that allows commands only on specific channels """

    def __init__(self, server, channels):
        self.channels = [find_channel(server, channel) for channel in channels]

    async def check(self, client, message, command):
        if not message.channel.is_private:
            if message.channel not in self.channels:
                raise PermissionDenied('invalid channel')
