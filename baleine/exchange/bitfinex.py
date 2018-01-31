from baleine import exchange, util


@exchange.register
class BitfinexExchange(exchange.Exchange):
    name = 'bitfinex'
    pairs = (
        ("BTC", "USD"), ("LTC", "USD"), ("LTC", "BTC"), ("ETH", "USD"),
        ("ETH", "BTC"), ("ETC", "BTC"), ("ETC", "USD"), ("RRT", "USD"),
        ("RRT", "BTC"), ("ZEC", "USD"), ("ZEC", "BTC"), ("XMR", "USD"),
        ("XMR", "BTC"), ("DSH", "USD"), ("DSH", "BTC"), ("BTC", "EUR"),
        ("XRP", "USD"), ("XRP", "BTC"), ("IOT", "USD"), ("IOT", "BTC"),
        ("IOT", "ETH"), ("EOS", "USD"), ("EOS", "BTC"), ("EOS", "ETH"),
        ("SAN", "USD"), ("SAN", "BTC"), ("SAN", "ETH"), ("OMG", "USD"),
        ("OMG", "BTC"), ("OMG", "ETH"), ("BCH", "USD"), ("BCH", "BTC"),
        ("BCH", "ETH"), ("NEO", "USD"), ("NEO", "BTC"), ("NEO", "ETH"),
        ("ETP", "USD"), ("ETP", "BTC"), ("ETP", "ETH"), ("QTM", "USD"),
        ("QTM", "BTC"), ("QTM", "ETH"), ("AVT", "USD"), ("AVT", "BTC"),
        ("AVT", "ETH"), ("EDO", "USD"), ("EDO", "BTC"), ("EDO", "ETH"),
        ("BTG", "USD"), ("BTG", "BTC"), ("DAT", "USD"), ("DAT", "BTC"),
        ("DAT", "ETH"), ("QSH", "USD"), ("QSH", "BTC"), ("QSH", "ETH"),
        ("YYW", "USD"), ("YYW", "BTC"), ("YYW", "ETH"), ("GNT", "USD"),
        ("GNT", "BTC"), ("GNT", "ETH"), ("SNT", "USD"), ("SNT", "BTC"),
        ("SNT", "ETH"), ("IOT", "EUR"),
    )

    UT_MAP = {
        1: '1m', 5: '5m', 15: '15m', 30: '30m',
        60: '1h', 180: '3h', 360: '6h', 720: '12h',
        1440: '1D', 10080: '7D', 20060: '14D', 43200: '1M',
    }

    API = 'https://api.bitfinex.com/v2'
    CHART_URL = '%s/candles/trade:{ut}:t{tickers[0]}{tickers[1]}/hist?limit={number}' % API
    BOOK_URL = '%s/book/t{tickers[0]}{tickers[1]}/P0/?len={depth}' % API
    TICKER_URL = '%s/ticker/t{tickers[0]}{tickers[1]}' % API

    async def fetch(self, url):
        async with util.http_session().get(url) as response:
            data = await response.json()
        if 'error' in data:
            raise IOError('Request failed: %s' % data['error'])
        return data

    async def get_pairs(self):
        return self.pairs

    async def get_chart_data(self, pair, ut, number):
        """ Return an iterable of TickerData """
        ut_param = self.UT_MAP.get(ut)
        if ut_param is None:
            raise ValueError('Invalid unit of time %s' % ut)

        data = await self.fetch(self.CHART_URL.format(tickers=pair, ut=ut_param, number=number))
        return [
            self.CandleData(time=item[0], open=item[1], close=item[2],
                            low=item[4], high=item[3], volume=item[5])
            for item in data[-number:]
        ]

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) OrderData """
        data = await self.fetch(self.BOOK_URL.format(tickers=pair, depth=100))

        return (
            [self.OrderData(price=item[0], amount=item[2]) for item in data if item[2] > 0],
            [self.OrderData(price=item[0], amount=-item[2]) for item in data if item[2] < 0],
        )

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        data = await self.fetch(self.TICKER_URL.format(tickers=pair))

        return self.TickerData(
            last=data[6],
            bid=data[0],
            ask=data[2],
            volume=data[7],
            change=data[5],
        )
