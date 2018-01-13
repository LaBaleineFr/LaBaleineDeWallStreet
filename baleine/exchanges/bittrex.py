import aiohttp
import pandas
import time
from baleine import exchange


@exchange.register
class BittrexExchange(exchange.Exchange):
    name = 'bittrex'

    API = 'https://bittrex.com/api/v1.1'
    PAIR_URL = '%s/public/getmarkets' % API
    BOOK_URL = '%s/public/getorderbook?market={tickers[1]}-{tickers[0]}&type=both' % API
    TICKER_URL = '%s/public/getmarketsummary?market={tickers[1]}-{tickers[0]}' % API

    async def get_pairs(self):
        timestamp = getattr(self, '_pairs_timestamp', None)
        if timestamp is None or timestamp + 3600 < time.time():
            response = await aiohttp.request('GET', self.PAIR_URL)
            data = await response.json()
            if not data.get('success', False):
                raise IOError('Request failed: %s' % data['message'])

            self._pairs = pairs = set(
                (item['MarketCurrency'], item['BaseCurrency'])
                for item in data['result']
            )
            self._pairs_timestamp = time.time()
        else:
            pairs = self._pairs
        return pairs

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        response = await aiohttp.request(
            'GET', self.BOOK_URL.format(tickers=pair, depth=depth)
        )
        data = await response.json()
        if not data.get('success'):
            raise IOError('Request failed: %s' % data.get('message'))

        data = data['result']
        df_asks = pd.DataFrame.from_dict(data['sell'])
        df_asks.rename(columns={'Rate': 'price', 'Quantity': 'ask'}, inplace=True)
        df_bids = pd.DataFrame.from_dict(data['buy'])
        df_bids.rename(columns={'Rate': 'price', 'Quantity': 'bid'}, inplace=True)
        # Cuz bittrex api is shitty
        df_bids = df_bids.head(depth)
        df_asks = df_asks.head(depth)
        return df_bids, df_asks

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        response = await aiohttp.request('GET', self.TICKER_URL.format(tickers=pair))
        data = await response.json()
        if not data.get('success'):
            raise IOError('Request failed: %s' % data.get('message'))

        data = data['result'][0]

        return exchange.TickerData(
            last=data['Last'],
            bid=data['Bid'],
            ask=data['Ask'],
            volume=data['Volume'],
            change=(data['Last'] - data['PrevDay']) / data['PrevDay'],
        )
