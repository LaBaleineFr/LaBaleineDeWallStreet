import asyncio
from baleine import command


class Id(command.Command):
    name = 'id-for'

    async def execute(self, message, args):
        if message.server is None:
            await self.error('only usable on a server')
            return
        if len(args) != 2:
            await self.error('%s type name' % self.name)
            return

        kind, name = args[0].lower(), args[1].lower()

        collections = {
            'channel': message.server.channels,
            'member': message.server.members,
            'role': message.server.roles,
        }
        items = collections.get(kind)

        if items is None:
            await self.error('known types: %s' % ', '.join(collections))
            return

        for item in items:
            if item.name.lower() == name:
                await self.send('{type} {name} has id {id}'.format(
                                type=kind, name=name, id=item.id))
                break
        else:
            await self.error('{type} {name} not found'.format(
                             type=kind, name=name))
