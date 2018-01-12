""" Command Group plugin

A command group is a set of commands that can be attached to a Bot instance.
It watches its designated channels and dispatches commands it recognizes.
"""
import logging
import shlex
from baleine.exception import PermissionDenied

logger = logging.getLogger(__name__)


class CommandGroup(object):
    allow_direct = True                 # Command group is usable in direct messages to bot
    channels = None                     # List of channels where group is available (None = all)
    prefixes = ['!', '#']

    permissions = []                    # List of permissions
    reply_class = None                  # How command writes its output

    enabled = True                      # If False, commands are not recognized

    def __init__(self, name):
        self.name = name
        self._commands = {}

    def register(self, name, command):
        self._commands[name] = command

    async def on_message(self, client, message):
        if not self.enabled:
            return

        # Ignore direct messages unless they are allowed
        if not self.allow_direct and message.channel.is_private:
            return

        # Ignore non-commands
        for prefix in self.prefixes:
            if message.content.startswith(prefix):
                text = message.content[len(prefix):]
                if not text:
                    return
                break
        else:
            return

        # If a channel list is specified ignore all messages in other chans
        if (self.channels is not None and not message.channel.is_private
                                      and message.channel.id not in self.channels):
            return

        output = self.reply_class(client, message)

        # Split message into arguments
        try:
            args = shlex.split(text)
            name = args.pop(0)
        except ValueError as exc:
            await output.error('malformed string')
            return

        # Fetch command to run
        name = name.lower()
        command_class = self._commands.get(name)
        if not command_class:
            return
        command = command_class(client, output)

        # Check command permissions
        try:
            await self.check_permissions(client, message, command)
        except PermissionDenied as exc:
            if getattr(exc, 'message', None) is not None:
                await output.error(exc.message)
            return

        # Run command and handle errors
        await output.start()
        try:
            await command.execute(message, args)
        except Exception:
            logger.exception(
                'Execution of command "{name}" with arguments ({args}) raised un handled exception',
                name=name,
                args=', '.join(repr(arg) for arg in args),
            )

    async def check_permissions(self, client, message, command):
        for permission in self.permissions:
            await permission.check(client, message, command)


class Command(object):
    def __init__(self, client, output):
        self.client = client
        self.output = output

    async def execute(self, message, args):
        raise NotImplementedError

    async def send(self, *args, **kwargs):
        await self.output.send(*args, **kwargs)

    async def error(self, *args, **kwargs):
        await self.output.error(*args, **kwargs)
