import time
from baleine import exchange, util


@exchange.register
class BittrexExchange(exchange.Exchange):
    name = 'bittrex'
    cache_time = 3600

    UT_MAP = {
        1: 'oneMin', 5: 'fiveMin', 30: 'thirtyMin', 60: 'hour', 1440: 'day',
    }

    API = 'https://bittrex.com/api/v1.1'
    PAIR_URL = '%s/public/getmarkets' % API
    CHART_URL = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={tickers[1]}-{tickers[0]}&tickInterval={ut}'
    BOOK_URL = '%s/public/getorderbook?market={tickers[1]}-{tickers[0]}&type=both' % API
    TICKER_URL = '%s/public/getmarketsummary?market={tickers[1]}-{tickers[0]}' % API

    async def fetch(self, url):
        async with util.http_session().get(url) as response:
            data = await response.json()
        if not data.get('success', False):
            raise IOError('Request failed: %s' % data['message'])
        return data['result']

    async def get_pairs(self):
        timestamp = getattr(self, '_pairs_timestamp', None)
        if timestamp is None or timestamp + self.cache_time < time.time():
            data = await self.fetch(self.PAIR_URL)
            self._pairs = pairs = set((item['MarketCurrency'], item['BaseCurrency'])
                                      for item in data)
            self._pairs_timestamp = time.time()
        else:
            pairs = self._pairs
        return pairs

    async def get_chart_data(self, pair, ut, number):
        """ Return an iterable of TickerData """
        ut_param = self.UT_MAP.get(ut)
        if ut_param is None:
            raise ValueError('Invalid unit of time %s' % ut)

        data = await self.fetch(self.CHART_URL.format(tickers=pair, ut=ut_param, number=number))
        return [
            self.CandleData(time=item['T'], open=item['O'], close=item['C'],
                            low=item['L'], high=item['H'], volume=item['V'])
            for item in data[-number:]
        ]

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        data = await self.fetch(self.BOOK_URL.format(tickers=pair, depth=depth))
        return (
            [self.OrderData(price=item['Rate'], amount=item['Quantity']) for item in data['buy'][:depth]],
            [self.OrderData(price=item['Rate'], amount=item['Quantity']) for item in data['sell'][:depth]]
        )

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        data = await self.fetch(self.TICKER_URL.format(tickers=pair))

        return self.TickerData(
            last=data[0]['Last'],
            bid=data[0]['Bid'],
            ask=data[0]['Ask'],
            volume=data[0]['Volume'],
            change=(data[0]['Last'] - data[0]['PrevDay']) / data[0]['PrevDay'],
        )
