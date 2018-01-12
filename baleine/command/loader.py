from importlib import import_module
from baleine.command import CommandGroup
from baleine.exception import ConfigurationError
from baleine.util import import_string

def load_group(server, config):
    """ Create a command group from a configuration dictionary """

    # First, setup the group
    group = CommandGroup(config.pop('name'))

    allow_direct = config.pop('allow_direct', None)
    if allow_direct is not None:
        group.allow_direct = allow_direct

    channels = config.pop('channels', None)
    if channels is not None:
        group.channels = map(find_channel(server, channel).id for channel in channels)

    prefixes = config.pop('prefixes', None)
    if prefixes is not None:
        group.prefixes = tuple(prefixes)

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
            group.permissions.append(klass(**entry))

    reply = config.pop('reply', 'DeleteAndMentionReply')
    if reply is not None:
        try:
            group.reply_class = import_string(reply)
        except ImportError:
            try:
                group.reply_class = import_string('baleine.command.reply.%s' % reply)
            except ImportError:
                raise ConfigurationError('Reply class %s not found' % reply)

    # Then load commands
    commands = config.pop('commands', None)
    if commands is None:
        raise ConfigurationError('Command group has no commands')

    if type(commands) == str:
        commands = [commands]
    for item in commands:
        enumerable = vars(import_module(item)).values()
        for entry in enumerable:
            if callable(entry) and hasattr(entry, 'execute'):
                group.register(entry.name, entry)

    # Check for mistyped entries
    if config:
        raise ConfigurationError(
            'Unkown configuration entries: %s' % ', '.join(config)
        )
    return group


def find_channel(server, text):
    for channel in server.channels:
        if text in (channel.name, channel.id):
            return channel
    raise ConfigurationError('Channel %s not found' % text)

def find_role(server, text):
    for role in server.roles:
        if text in (role.name, role.id):
            return role
    raise ConfigurationError('Role %s not found' % text)
