import asyncio
import shlex


class CommandDispatcher(object):
    """ Bot plugin that dispatches user commands to command groups.
        baleine.bot.Bot automatically creates one per server.
    """

    prefixes = tuple('!#')
    delete_errors_after = 5

    def __init__(self, server):
        self.server = server
        self.groups = []

    async def on_message(self, client, message):
        # Filter out messages to other servers
        if message.server and message.server.id != self.server.id:
            return

        # Filter non-commands early
        if not message.content.startswith(self.prefixes):
            return
        text = message.content[1:]

        # Split message into arguments, taking quotes into accout (foo "bar baz") is 2 args
        try:
            args = shlex.split(text)
            name = args.pop(0).lower()
        except (ValueError, IndexError):
            await self.handle_basic_error(client, message, 'format de commande incorrect')
            return

        # Dispatch to enabled command groups
        for group in self.groups:
            if group.enabled and name in group.commands:
                await group.on_command(client, message, name, args)
                break
        else:
            await self.handle_basic_error(client, message, 'commande inconnue %s' % name)

    async def handle_basic_error(self, client, message, text):
        # Send the error
        if not message.channel.is_private:
            text = '%s: %s' % (message.author.mention, text)
        answer = await client.send_message(message.channel, text)

        # Wait for a bit and delete the error so as not to pollute the channel
        if not message.channel.is_private and self.delete_errors_after is not None:
            await asyncio.sleep(self.delete_errors_after, client.loop)
            await asyncio.gather(
                client.delete_message(message),
                client.delete_message(answer),
                return_exceptions=True,
                loop=client.loop
            )
