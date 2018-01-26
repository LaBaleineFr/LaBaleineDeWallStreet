import asyncio
import discord
import shlex


class CommandDispatcher(object):
    """ Bot plugin that dispatches user commands to command groups.
        baleine.bot.Bot automatically creates one per guild.
    """

    prefixes = tuple('!#')
    delete_errors_after = 5

    def __init__(self, guild):
        self.guild = guild
        self.groups = []

    async def on_message(self, client, message):
        # Filter out messages to other guilds
        if message.guild and message.guild.id != self.guild.id:
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
        if not isinstance(message.channel, discord.DMChannel):
            text = '%s: %s' % (message.author.mention, text)
        answer = await message.channel.send(text)

        # Wait for a bit and delete the error so as not to pollute the channel
        if isinstance(message.channel, discord.abc.GuildChannel) and self.delete_errors_after is not None:
            await asyncio.sleep(self.delete_errors_after, client.loop)
            await asyncio.gather(message.delete(), answer.delete(),
                                 return_exceptions=True, loop=client.loop)
