from importlib import import_module
from baleine.command import CommandGroup, Command
from baleine.exception import ConfigurationError
from baleine.util import import_string, find_channel


def load_group(server, config):
    """ Create a CommandGroup for given server using given configuraiton dictionary """

    config = config.copy()
    group = CommandGroup(config.pop('name'))

    # Simple parameters

    allow_direct = config.pop('allow_direct', None)
    if allow_direct is not None:
        group.allow_direct = allow_direct

    channels = config.pop('channels', None)
    if channels is not None:
        group.channels = map(find_channel(server, channel).id for channel in channels)

    prefixes = config.pop('prefixes', None)
    if prefixes is not None:
        group.prefixes = tuple(prefixes)

    # Permissions are configurable class instances that we must import

    permissions = config.pop('permissions', None)
    if permissions is not None:
        for entry in permissions:
            name = entry.pop('name')
            try:
                klass = import_string(name)
            except ImportError:
                try:
                    klass = import_string('baleine.command.permission.%s' % name)
                except ImportError:
                    raise ConfigurationError('Permission class %s not found' % name)
            group.permissions.append(klass(server, **entry))

    # Reply is a class that we must import

    reply = config.pop('reply', 'DeleteAndMentionReply')
    if reply is not None:
        try:
            group.reply_class = import_string(reply)
        except ImportError:
            try:
                group.reply_class = import_string('baleine.command.reply.%s' % reply)
            except ImportError:
                raise ConfigurationError('Reply class %s not found' % reply)

    # Commands are module name, we locate Command subclasses in the module

    commands = config.pop('commands', None)
    if commands is None:
        raise ConfigurationError('Command group has no commands')

    if type(commands) == str:
        commands = [commands]
    for item in commands:
        enumerable = vars(import_module(item)).values()
        for entry in enumerable:
            if isinstance(entry, type) and issubclass(entry, Command):
                group.register(entry.name, entry)

    # Check for mistyped entries
    if config:
        raise ConfigurationError(
            'Unkown configuration entries: %s' % ', '.join(config)
        )
    return group
