import asyncio
# Reply objects abstract out how commands generate output

class Reply(object):
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
        await self.send(text)

    async def do_send(self, destination, content, embed=None, fileobj=None, filename=None):
        if fileobj is None:
            await self.client.send_message(destination, content, embed=embed)
        else:
            await self.client.send_file(destination, fileobj, content=content, filename=filename)


class DirectReply(Reply):
    """ Reply object that send answers back through a direct message """

    async def notify(self):
        await self.client.send_typing(self.user)

    async def send(self, text, embed=None, fileobj=None, filename=None):
        if not self.channel.is_private:
            asyncio.ensure_future(self.client.delete_message(self.message), loop=self.client.loop)
        await self.do_send(self.user, content=text, embed=embed, fileobj=fileobj, filename=filename)


class MentionReply(Reply):
    """ Reply object that send answers back through originating channel """

    async def notify(self):
        await self.client.send_typing(self.user)

    async def send(self, text, embed=None, fileobj=None, filename=None):
        if not self.channel.is_private:
            text = '%s: %s' % (self.user.mention, text)
        await self.do_send(
            self.channel,
            content=text,
            embed=embed,
            fileobj=fileobj,
            filename=filename,
        )

class DeleteAndMentionReply(MentionReply):
    """ Reply object that send answers back through originating channel """

    async def start(self):
        asyncio.ensure_future(self.client.delete_message(self.message), loop=self.client.loop)
