import aiohttp
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

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        if not pair in self.pairs:
            raise ValueError('Invalid pair')

        now = time.time()
        cache_time = getattr(self, '_cache_time', None)
        if not cache_time or cache_time + self.CACHE_TIME < now:
            response = await aiohttp.request('GET', self.TICKER_URL)
            data = self._data = (await response.json())['rates']
            self._cache_time = now
        else:
            data = self._data

        return exchange.TickerData(
            last=data[pair[1]],
            bid=data[pair[1]],
            ask=data[pair[1]],
            volume=0,
            change=0,
        )
