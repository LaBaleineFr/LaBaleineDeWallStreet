import asyncio
from baleine import exception


class PrivateChat(object):
    """ A direct messaging channel to a specific user
        There should be only one per user per bot. The intent is to provide a way for
        multiple plugins to claim, acquire and release the private chat, preventing
        several of them from interacting simultaneously and confusing the user.
    """

    def __init__(self, client, user):
        self.client = client
        self.user = user
        self.channel = None
        self.task = None

    async def wait_reply(self, timeout=None):
        """ Wait until the user types something or specified time elapses (in seconds)
            Calling task must have acquired ownership of the channel first.
        """
        assert self.task == asyncio.Task.current_task()

        def check(msg):
            return msg.channel == self.channel and msg.author == self.user
        return await self.client.wait_for('message', check=check, timeout=timeout)

    async def send(self, *args, **kwargs):
        """ Send a message to the user """
        return await self.user.send(*args, **kwargs)

    async def __aenter__(self):
        """ Acquire ownership of the private chat """
        if self.task:
            raise exception.BusyError()
        self.task = asyncio.Task.current_task()
        if not self.channel:
            self.channel = await self.user.create_dm()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """ Release ownership of the private chat """
        self.task = None
