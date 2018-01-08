import asyncio
from collections import namedtuple

TickerData = namedtuple('TickerData', 'last bid ask volume change')


class Exchange(object):
    name = None
    pairs = ()

    @asyncio.coroutine
    def get_order_book(self, pair, depth):
        """ Return a 2-tuple of (bid, ask) data frames """
        raise NotImplementedError()

    @asyncio.coroutine
    def get_prices(self, pair):
        """ Return a TickerData instance """
        raise NotImplementedError()


EXCHANGE_CLASSES = []
def register(cls):
    EXCHANGE_CLASSES.append(cls)
    return cls

def get(name):
    for klass in EXCHANGE_CLASSES:
        if klass.name == name:
            return klass()
    raise KeyError('Exchange %r is not supported' % (name, ))

def pair(name):
    for klass in EXCHANGE_CLASSES:
        if name in klass.pairs:
            return klass()
    raise ValueError('Pair %r is not supported by any known exchange' % (name, ))
