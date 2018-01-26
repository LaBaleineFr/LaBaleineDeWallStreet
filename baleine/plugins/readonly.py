import asyncio
import baleine.bot
import logging

logger = logging.getLogger(__name__)

class ReadOnly(object):
    """ Simple plugin that unconditionnaly deletes any message sent to some channels """

    channels = None
    whitelist = None

    def __init__(self, config):
        try:
            channels = config['channels']
        except KeyError:
            raise baleine.bot.ConfigError('ReadOnly plugin requires a channels list')
        self.channels = [int(channel) for channel in config['channels']]

        self.whitelist = [item.lower() for item in config.get('whitelist') or []]

    async def on_message(self, client, message):
        if (message.channel and message.channel.id in self.channels and
            not message.author.bot and
            not any(role.name.lower() in self.whitelist for role in message.author.roles)):

            # Fire and forget, we don't want this to delay command execution
            asyncio.ensure_future(self.delete_message(message), loop=client.loop)

    async def delete_message(self, message):
        try:
            await message.delete()
        except discord.NotFound:
            pass # this is okay, message is already deleted
        except discord.HTTPException as exc:
            logger.warning('could not delete message in channel %s: %s' % (message.channel.name, exc))
