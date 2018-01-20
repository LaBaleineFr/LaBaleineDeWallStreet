import asyncio
import baleine.bot

class ReadOnly(object):
    def __init__(self, config):
        try:
            channels = config['channels']
        except KeyError:
            raise baleine.bot.ConfigError('ReadOnly plugin requires a channels list')

        self.channels = [str(channel) for channel in config['channels']]

    async def on_message(self, client, message):
        if message.channel.id in self.channels:
            asyncio.ensure_future(self.delete_message(client, message), loop=client.loop)

    async def delete_message(self, client, message):
        try:
            await client.delete_message(message)
        except discord.errors.NotFound:
            pass
        except discord.errors.HTTPException as exc:
            logger.warning('could not delete message in channel %s: %s' % (message.channel.name, exc))
