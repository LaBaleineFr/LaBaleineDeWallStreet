import asyncio
import baleine.bot

class ReadOnly(object):
    def __init__(self, config):
        try:
            channels = config['channels']
        except KeyError:
            raise baleine.bot.ConfigError('ReadOnly plugin requires a channels list')

        self.channels = [str(channel) for channel in config['channels']]

    @asyncio.coroutine
    def on_message(self, client, message):
        if message.channel.id in self.channels:
            yield from client.delete_message(message)
