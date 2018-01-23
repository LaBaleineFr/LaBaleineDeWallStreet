import asyncio
from collections import namedtuple

CandleData = namedtuple('CandleData', 'time open close low high volume')
OrderData = namedtuple('OrderData', 'price amount')
TickerData = namedtuple('TickerData', 'last bid ask volume change')


class Exchange(object):
    """ Abstract class  for reference - exchange plugins should derive from it """
    name = None     # Lowercase name for the exchange

    async def get_pairs(self):
        """ Return an iterable of 2-tuple of tickers """
        raise NotImplementedError()

    async def get_chart_data(self, pair, ut, number):
        """ Return an iterable of CandleData """
        raise NotImplementedError()

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) OrderData """
        raise NotImplementedError()

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        raise NotImplementedError()


EXCHANGES = []
def register(cls):
    EXCHANGES.append(cls())
    return cls

def get(name):
    """ Return exchange with given name """
    for xchg in EXCHANGES:
        if xchg.name == name:
            return xchg
    raise KeyError('Exchange %r is not supported' % (name, ))

# Simple helper function that returns an exchange along with its pairs
async def get_exchange_pairs(xchg):
    return xchg, await xchg.get_pairs()

async def pair(name, timeout=None):
    """ Return an exchange that supports the given pair """

    # As those can be a bit long, we fire them in parallel and use the first matching result
    tasks = [get_exchange_pairs(xchg) for xchg in EXCHANGES]
    for task in asyncio.as_completed(tasks, timeout=timeout):
        xchg, pairs = await task
        if name in pairs:
            return xchg

    raise ValueError('Pair %r is not supported by any known exchange' % (name, ))
