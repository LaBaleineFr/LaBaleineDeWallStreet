import asyncio
from baleine.command import Command
from baleine.exception import ConfigurationError

class File(Command):
    private_reply = True

    def __init__(self, settings):
        try:
            self.path = settings.pop('file')
        except KeyError:
            raise ConfigurationError('Missing file for file plugin')
        self.private_reply = settings.pop('private_reply', self.private_reply)
        super().__init__(settings)

    @property
    def content(self):
        data = getattr(self, '_content', None)
        if not data:
            with open(self.path, 'r') as fd:
                data = self._content = fd.read()
        return data

    @asyncio.coroutine
    def execute(self, client, message, args):
        yield from client.send_message(
            message.author if self.private_reply else message.channel,
            self.content
        )
