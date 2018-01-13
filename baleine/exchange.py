import asyncio
from collections import namedtuple

TickerData = namedtuple('TickerData', 'last bid ask volume change')


class Exchange(object):
    name = None

    async def get_pairs(self):
        """ Return an iterable of 2-tuple of tickers """
        raise NotImplementedError()

    async def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        raise NotImplementedError()

    async def get_prices(self, pair):
        """ Return a TickerData instance """
        raise NotImplementedError()


EXCHANGES = []
def register(cls):
    EXCHANGES.append(cls())
    return cls

def get(name):
    for xchg in EXCHANGES:
        if xchg.name == name:
            return xchg
    raise KeyError('Exchange %r is not supported' % (name, ))

async def pair(name):
    for xchg in EXCHANGES:
        if name in await xchg.get_pairs():
            return xchg
    raise ValueError('Pair %r is not supported by any known exchange' % (name, ))
