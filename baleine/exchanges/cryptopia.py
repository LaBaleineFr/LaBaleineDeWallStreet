import time
from baleine import exchange, util


@exchange.register
class CryptopiaExchange(exchange.Exchange):
    name = 'cryptopia'
    cache_time = 3600

    API = 'https://www.cryptopia.co.nz/api'
    CHART_URL = 'https://www.cryptopia.co.nz/Exchange/GetTradePairChart?tradePairId={pairid}&dataRange=1&dataGroup={ut}'
    PAIR_URL = '%s/GetTradePairs' % API
    BOOK_URL = '%s/GetMarketOrders/{tickers[0]}_{tickers[1]}/{depth}' % API
    TICKER_URL = '%s/GetMarket/{tickers[0]}_{tickers[1]}' % API

    async def fetch(self, url, key='Data'):
        async with util.http_session().get(url) as response:
            data = await response.json()
        if data.get('Error', None):
            raise IOError('Request failed: %s' % data['Error'])
        return data[key] if key else data

    async def get_pairs(self):
        timestamp = getattr(self, '_pairs_timestamp', None)
        if timestamp is None or timestamp + self.cache_time < time.time():
            data = await self.fetch(self.PAIR_URL)
            self._pairs = pairs = set(
                (item['Symbol'], item['BaseSymbol'])
                for item in data
            )
            self._pair_ids = dict(
                ((item['Symbol'], item['BaseSymbol']), item['Id'])
                for item in data
            )
            self._pairs_timestamp = time.time()
        else:
            pairs = self._pairs
        return pairs

    async def get_chart_data(self, pair, ut, number):
        """ Return an iterable of TickerData """

        await self.get_pairs()  # ensure pairs are loaded, we need the id
        data = await self.fetch(self.CHART_URL.format(pairid=self._pair_ids[pair], ut=ut), key=None)

        volumes = dict((int(item['x']), item['y']) for item in data['Volume'])

        return [
            exchange.CandleData(time=item[0], open=item[1], close=item[4],
                                low=item[3], high=item[2], volume=volumes.get(int(item[0])))
            for item in data['Candle'][-number:]
        ]

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        data = await self.fetch(self.BOOK_URL.format(tickers=pair, depth=depth))
        return (
            [exchange.OrderData(price=item['Price'], amount=item['Volume']) for item in data['Sell']],
            [exchange.OrderData(price=item['Price'], amount=item['Volume']) for item in data['Buy']],
        )

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        data = await self.fetch(self.TICKER_URL.format(tickers=pair))
        return exchange.TickerData(
            last=data['LastPrice'],
            bid=data['BidPrice'],
            ask=data['AskPrice'],
            volume=data['Volume'],
            change=data['Change']/100,
        )
