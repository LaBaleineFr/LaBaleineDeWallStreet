import asyncio
from baleine import exception


class PrivateChat(object):
    def __init__(self, client, user):
        self.client = client
        self.user = user
        self.channel = None
        self.task = None

    async def wait_reply(self, timeout=None):
        assert self.task == asyncio.Task.current_task()
        return await self.client.wait_for_message(timeout=timeout, author=self.user, channel=self.channel)

    async def send(self, *args, **kwargs):
        return await self.client.send_message(self.user, *args, **kwargs)

    async def __aenter__(self):
        """ Acquire ownership of the private chat """
        if self.task:
            raise exception.BusyError()
        self.task = asyncio.Task.current_task()
        if not self.channel:
            self.channel = await self.client.start_private_message(self.user)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """ Release ownership of the private chat """
        self.task = None
