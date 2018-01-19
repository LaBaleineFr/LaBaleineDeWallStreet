import pandas
import time
from baleine import exchange, util


@exchange.register
class CryptopiaExchange(exchange.Exchange):
    name = 'cryptopia'
    cache_time = 3600

    API = 'https://www.cryptopia.co.nz/api'
    PAIR_URL = '%s/GetTradePairs' % API
    BOOK_URL = '%s/GetMarketOrders/{tickers[0]}_{tickers[1]}/{depth}' % API
    TICKER_URL = '%s/GetMarket/{tickers[0]}_{tickers[1]}' % API

    async def get_pairs(self):
        timestamp = getattr(self, '_pairs_timestamp', None)
        if timestamp is None or timestamp + 3600 < time.time():
            async with util.http_session().get(self.PAIR_URL) as response:
                data = await response.json()
            if not data.get('Success', False):
                raise IOError('Request failed: %s' % data['Message'])

            self._pairs = pairs = set(
                (item['Symbol'], item['BaseSymbol'])
                for item in data['Data']
            )
            self._pairs_timestamp = time.time()
        else:
            pairs = self._pairs
        return pairs

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        async with util.http_session().get(self.BOOK_URL.format(tickers=pair, depth=depth)) as response:
            data = await response.json()
        if not data.get('Success', False):
            raise IOError('Request failed: %s' % data['Message'])

        data = data['Data']
        df_asks = pd.DataFrame.from_dict(data['Sell'])
        df_asks.rename(columns={'Price': 'price', 'Volume': 'ask'}, inplace=True)
        df_bids = pd.DataFrame.from_dict(data['Buy'])
        df_bids.rename(columns={'Price': 'price', 'Volume': 'bid'}, inplace=True)
        return df_bids, df_asks

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        async with util.http_session().get(self.TICKER_URL.format(tickers=pair)) as response:
            data = await response.json()
        if not data.get('Success', False):
            raise IOError('Request failed: %s' % data['Message'])

        data = data['Data']
        return exchange.TickerData(
            last=data['LastPrice'],
            bid=data['BidPrice'],
            ask=data['AskPrice'],
            volume=data['Volume'],
            change=data['Change']/100,
        )
