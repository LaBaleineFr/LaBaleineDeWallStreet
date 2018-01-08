import argparse
import asyncio
import logging
import shlex
from baleine.exception import ConfigurationError

logger = logging.getLogger(__name__)

class Command(object):
    command = ()
    prefixes = ('!', '#')

    allow_direct = True
    channels = None         # None -> no filter / [] -> allowed nowhere
    delete_command = True

    def __init__(self, settings):
        self.command = settings.pop('command', list(self.command or ()))
        if not self.command:
            raise ValueError('Command name empty or undefined')

        self.allow_direct = settings.pop('allow_direct', self.allow_direct)
        self.channels = settings.pop('channels', self.channels)
        self.delete_command = settings.pop('delete_command', self.delete_command)
        if settings:
            raise ConfigurationError('Unknown parameters: %s' % ', '.join(settings))

    @asyncio.coroutine
    def on_message(self, client, message):
        if self.should_ignore_message(message):
            return

        args = shlex.split(message.content[1:] if message.content.startswith(self.prefixes)
                           else message.content)
        cmd = args[0].lower().lstrip('!').lstrip('#')
        if cmd not in self.command:
            return

        yield from self.execute(client, message, args[1:])
        if self.delete_command:
            yield from client.delete_message(message)

    def should_ignore_message(self, message):
        if message.author.bot:
            return True
        if not message.channel.is_private and not message.content.startswith(self.prefixes):
            return True
        if message.channel.is_private and not self.allow_direct:
            return True
        if self.channels is not None and message.channel.id not in self.channels:
            return True
        return False

    @asyncio.coroutine
    def execute(self, client, message, args):
        raise NotImplementedError()
