""" Command Group plugin

A command group is a set of commands that can be attached to a dispatcher.
It watches its designated channels and runs commands it recognizes.
"""
import logging
from baleine.exception import PermissionDenied

logger = logging.getLogger(__name__)


class CommandGroup(object):
    allow_direct = True                 # Command group is usable in direct messages to bot
    channels = None                     # List of channels where group is available (None = all)

    permissions = []                    # List of permissions
    reply_class = None                  # How command writes its output

    enabled = True                      # If False, commands are not recognized

    def __init__(self, name):
        self.name = name
        self.commands = {}

    def register(self, name, command):
        self.commands[name] = command

    async def on_command(self, client, message, name, args):
        # Ignore direct messages unless they are allowed
        if not self.allow_direct and message.channel.is_private:
            return

        # If a channel list is specified ignore all messages in other chans
        if (self.channels is not None and not message.channel.is_private
                                      and message.channel.id not in self.channels):
            return

        output = self.reply_class(client, message)

        # Fetch command to run
        command_class = self.commands.get(name)
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
