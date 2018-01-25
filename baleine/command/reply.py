import asyncio
import discord
import logging

logger = logging.getLogger(__name__)


class Reply(object):
    """ Abstract out the way commands generate output """

    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.server = message.server
        self.channel = message.channel
        self.user = message.author

    async def start(self):
        pass

    async def notify(self):
        pass

    async def send(self, text, embed=None, fileobj=None, filename=None):
        raise NotImplementedError

    async def error(self, text):
        return await self.send(text)

    async def do_send(self, destination, content, embed=None, fileobj=None, filename=None):
        if fileobj is None:
            return await self.client.send_message(destination, content, embed=embed)
        else:
            return await self.client.send_file(destination, fileobj, content=content, filename=filename)

    async def delete_message(self, message):
        try:
            await self.client.delete_message(message)
        except discord.errors.NotFound:
            pass
        except discord.errors.HTTPException as exc:
            logger.warning('could not delete message in channel %s: %s' % (message.channel.name, exc))


class DirectReply(Reply):
    """ Reply object that send answers back through a direct message """

    async def notify(self):
        await self.client.send_typing(self.user)

    async def send(self, text, embed=None, fileobj=None, filename=None):
        if not self.channel.is_private:
            asyncio.ensure_future(self.delete_message(self.message), loop=self.client.loop)
        return await self.do_send(self.user, content=text,
                                  embed=embed, fileobj=fileobj, filename=filename)


class MentionReply(Reply):
    """ Reply object that send answers back through originating channel """

    async def notify(self):
        await self.client.send_typing(self.user)

    async def send(self, text, embed=None, fileobj=None, filename=None):
        if not self.channel.is_private:
            text = '%s: %s' % (self.user.mention, text)
        return await self.do_send(
            self.channel,
            content=text,
            embed=embed,
            fileobj=fileobj,
            filename=filename,
        )

class DeleteAndMentionReply(MentionReply):
    """ Reply object that send answers back through originating channel """

    async def start(self):
        if not self.channel.is_private:
            asyncio.ensure_future(self.delete_message(self.message), loop=self.client.loop)

    async def error(self, text):
        message = await self.send(text)
        if not self.channel.is_private:
            asyncio.ensure_future(self.delete_after(message, 10), loop=self.client.loop)
        return message

    async def delete_after(self, message, delay):
        await asyncio.sleep(delay, loop=self.client.loop)
        await self.delete_message(message)
