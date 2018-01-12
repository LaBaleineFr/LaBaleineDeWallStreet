from baleine.exception import PermissionDenied


class HasRolePermission(object):
    """ Permission that allows commands only for specific roles """

    def __init__(self, roles):
        self.id_list = roles

    async def check(self, client, message, command):
        for role_id in self.id_list:
            if role_id in message.author.roles:
                return
        raise PermissionDenied('forbidden')


class ChannelWhitelistPermission(object):
    """ Permission that allows commands only on specific channels """

    def __init__(self, channels):
        self.id_list = channels

    async def check(self, client, message, command):
        if not message.channel.is_private:
            if message.channel.id not in self.id_list:
                raise PermissionDenied('invalid channel')
