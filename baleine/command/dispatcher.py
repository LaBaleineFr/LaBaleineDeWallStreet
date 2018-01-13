import asyncio
import shlex


class CommandDispatcher(object):
    prefixes = tuple('!#')
    delete_errors_after = 5

    def __init__(self, server):
        self.server = server
        self.groups = []

    async def on_message(self, client, message):
        if message.server.id != self.server.id:
            return

        # Filter non-commands early
        if not message.content.startswith(self.prefixes):
            return
        text = message.content[1:]

        try:
            args = shlex.split(text)
            name = args.pop(0).lower()
        except (ValueError, IndexError):
            await self.handle_basic_error(client, message, 'format de commande incorrect')
            return

        for group in self.groups:
            if group.enabled and name in group.commands:
                await group.on_command(client, message, name, args)
                break
        else:
            await self.handle_basic_error(client, message, 'commande inconnue %s' % name)

    async def handle_basic_error(self, client, message, text):
        if not message.channel.is_private:
            text = '%s: %s' % (message.author.mention, text)
        answer = await client.send_message(message.channel, text)

        if not message.channel.is_private and self.delete_errors_after is not None:
            await asyncio.sleep(self.delete_errors_after, client.loop)
            await asyncio.gather(
                client.delete_message(message),
                client.delete_message(answer),
                return_exceptions=True,
                loop=client.loop
            )
