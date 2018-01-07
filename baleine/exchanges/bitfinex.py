import aiohttp
import asyncio
import pandas
from baleine import exchange


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

    API = 'https://api.bitfinex.com/v2'
    BOOK_URL = '%s/book/t{tickers[0]}{tickers[1]}/P0/?len={depth}' % API
    TICKER_URL = '%s/ticker/t{tickers[0]}{tickers[1]}' % API

    @asyncio.coroutine
    def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        response = yield from aiohttp.request(
            'GET', self.BOOK_URL.format(tickers=pair, depth=depth)
        )
        data = yield from response.json()
        if 'error' in data:
            raise IOError('Request failed: %s' % data['error'])

        df = pandas.DataFrame.from_dict(data)
        df.rename(columns={0: 'price', 1: 'count', 2: 'amount'}, inplace=True)
        df_asks = df[['price', 'amount']][df['amount'] < 0]
        df_asks = df_asks.abs()
        df_bids = df[['price', 'amount']][df['amount'] > 0]
        df_asks.rename(columns={'amount': 'ask'}, inplace=True)
        df_bids.rename(columns={'amount': 'bid'}, inplace=True)
        return df_bids, df_asks

    @asyncio.coroutine
    def get_prices(self, pair):
        """ Return a TickerData instance """
        response = yield from aiohttp.request('GET', self.TICKER_URL.format(tickers=pair))
        data = yield from response.json()

        return exchange.TickerData(
            last=data[6],
            bid=data[0],
            ask=data[2],
            volume=data[7],
            change=data[5],
        )
