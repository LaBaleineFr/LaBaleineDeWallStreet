import asyncio
import time
from baleine import exchange


@exchange.register
class ForexExchange(exchange.Exchange):
    name = 'forex'
    pairs = (
        ("USD", "EUR"), ("USD", "CHF"), ("USD", "GBP"), ("USD", "CAD"), ("USD", "JPY"),
    )

    CACHE_TIME = 3600
    API = 'https://api.fixer.io/'
    TICKER_URL = '%s/latest?base=USD' % API

    async def get_pairs(self):
        return self.pairs

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        if pair not in self.pairs:
            raise ValueError('Invalid pair')

        now = time.time()
        cache_time = getattr(self, '_cache_time', None)
        if not cache_time or cache_time + self.CACHE_TIME < now:
            async with util.http_session().get(self.TICKER_URL) as response:
                data = self._data = (await response.json())['rates']
            self._cache_time = now
        else:
            data = self._data

        return self.TickerData(
            last=data[pair[1]],
            bid=data[pair[1]],
            ask=data[pair[1]],
            volume=0,
            change=0,
        )
