""" Command Group plugin

A command group is a set of commands that can be attached to a dispatcher.
It watches its designated channels and runs commands it recognizes.
"""
import asyncio
import logging
import shlex
from baleine.exception import PermissionDenied

logger = logging.getLogger(__name__)


class CommandGroup(object):
    allow_direct = True                 # Command group is usable in direct messages to bot
    channels = None                     # List of channels where group is available (None = all)

    permissions = None                  # List of permissions
    reply_class = None                  # How command writes its output

    enabled = True                      # If False, commands are not recognized

    def __init__(self, name):
        self.name = name
        self.permissions = []
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
        logger.info('{user} [{userid}] runs  {name} {args}'.format(
            user=message.author.name,
            userid=message.author.id,
            name=name,
            args=' '.join(shlex.quote(arg) for arg in args),
        ))
        await output.start()
        try:
            await command.execute(message, args)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception(
                'Execution of command "{name}" with arguments ({args}) raised unhandled exception'
                .format(name=name, args=', '.join(repr(arg) for arg in args))
            )

    async def check_permissions(self, client, message, command):
        """ Raise baleine.exception.PermissionDenied if command is not allowed """
        for permission in self.permissions:
            await permission.check(client, message, command)


class Command(object):
    """ Single abstract command, inherited by commands """
    name = None
    errors = {}

    def __init__(self, client, output):
        self.client = client
        self.output = output

    async def execute(self, message, args):
        """ Execute the command with given arguments in message's context """
        raise NotImplementedError

    async def send(self, *args, **kwargs):
        """ Send output to command initiator - arguments are passed through to output plugin """
        await self.output.send(*args, **kwargs)

    async def error(self, error, *args, **kwargs):
        """ Send error to command initiator - arguments are formatted with the error message """
        await self.output.error(self.errors[error].format(*args, **kwargs))
