import aiohttp
import pandas
from baleine import exchange


@exchange.register
class BittrexExchange(exchange.Exchange):
    name = 'bittrex'
    pairs = (   # TODO: replace with dynamic query to exchange
        ("LTC", "BTC"), ("DOGE", "BTC"), ("VTC", "BTC"), ("PPC", "BTC"),
        ("FTC", "BTC"), ("RDD", "BTC"), ("NXT", "BTC"), ("DASH", "BTC"),
        ("POT", "BTC"), ("BLK", "BTC"), ("EMC2", "BTC"), ("XMY", "BTC"),
        ("AUR", "BTC"), ("EFL", "BTC"), ("GLD", "BTC"), ("SLR", "BTC"),
        ("PTC", "BTC"), ("GRS", "BTC"), ("NLG", "BTC"), ("RBY", "BTC"),
        ("XWC", "BTC"), ("MONA", "BTC"), ("THC", "BTC"), ("ENRG", "BTC"),
        ("ERC", "BTC"), ("VRC", "BTC"), ("CURE", "BTC"), ("XMR", "BTC"),
        ("CLOAK", "BTC"), ("START", "BTC"), ("KORE", "BTC"), ("XDN", "BTC"),
        ("TRUST", "BTC"), ("NAV", "BTC"), ("XST", "BTC"), ("BTCD", "BTC"),
        ("VIA", "BTC"), ("PINK", "BTC"), ("IOC", "BTC"), ("CANN", "BTC"),
        ("SYS", "BTC"), ("NEOS", "BTC"), ("DGB", "BTC"), ("BURST", "BTC"),
        ("EXCL", "BTC"), ("SWIFT", "BTC"), ("DOPE", "BTC"), ("BLOCK", "BTC"),
        ("ABY", "BTC"), ("BYC", "BTC"), ("XMG", "BTC"), ("BLITZ", "BTC"),
        ("BAY", "BTC"), ("FAIR", "BTC"), ("SPR", "BTC"), ("VTR", "BTC"),
        ("XRP", "BTC"), ("GAME", "BTC"), ("COVAL", "BTC"), ("NXS", "BTC"),
        ("XCP", "BTC"), ("BITB", "BTC"), ("GEO", "BTC"), ("FLDC", "BTC"),
        ("GRC", "BTC"), ("FLO", "BTC"), ("NBT", "BTC"), ("MUE", "BTC"),
        ("XEM", "BTC"), ("CLAM", "BTC"), ("DMD", "BTC"), ("GAM", "BTC"),
        ("SPHR", "BTC"), ("OK", "BTC"), ("SNRG", "BTC"), ("PKB", "BTC"),
        ("CPC", "BTC"), ("AEON", "BTC"), ("ETH", "BTC"), ("GCR", "BTC"),
        ("TX", "BTC"), ("BCY", "BTC"), ("EXP", "BTC"), ("INFX", "BTC"),
        ("OMNI", "BTC"), ("AMP", "BTC"), ("AGRS", "BTC"), ("XLM", "BTC"),
        ("BTC", "USDT"), ("CLUB", "BTC"), ("VOX", "BTC"), ("EMC", "BTC"),
        ("FCT", "BTC"), ("MAID", "BTC"), ("EGC", "BTC"), ("SLS", "BTC"),
        ("RADS", "BTC"), ("DCR", "BTC"), ("BSD", "BTC"), ("XVG", "BTC"),
        ("PIVX", "BTC"), ("XVC", "BTC"), ("MEME", "BTC"), ("STEEM", "BTC"),
        ("2GIVE", "BTC"), ("LSK", "BTC"), ("PDC", "BTC"), ("BRK", "BTC"),
        ("DGD", "BTC"), ("DGD", "ETH"), ("WAVES", "BTC"), ("RISE", "BTC"),
        ("LBC", "BTC"), ("SBD", "BTC"), ("BRX", "BTC"), ("ETC", "BTC"),
        ("ETC", "ETH"), ("STRAT", "BTC"), ("UNB", "BTC"), ("SYNX", "BTC"),
        ("TRIG", "BTC"), ("EBST", "BTC"), ("VRM", "BTC"), ("SEQ", "BTC"),
        ("REP", "BTC"), ("SHIFT", "BTC"), ("ARDR", "BTC"), ("XZC", "BTC"),
        ("NEO", "BTC"), ("ZEC", "BTC"), ("ZCL", "BTC"), ("IOP", "BTC"),
        ("GOLOS", "BTC"), ("UBQ", "BTC"), ("KMD", "BTC"), ("GBG", "BTC"),
        ("SIB", "BTC"), ("ION", "BTC"), ("LMC", "BTC"), ("QWARK", "BTC"),
        ("CRW", "BTC"), ("SWT", "BTC"), ("MLN", "BTC"), ("ARK", "BTC"),
        ("DYN", "BTC"), ("TKS", "BTC"), ("MUSIC", "BTC"), ("DTB", "BTC"),
        ("INCNT", "BTC"), ("GBYTE", "BTC"), ("GNT", "BTC"), ("NXC", "BTC"),
        ("EDG", "BTC"), ("LGD", "BTC"), ("TRST", "BTC"), ("GNT", "ETH"),
        ("REP", "ETH"), ("ETH", "USDT"), ("WINGS", "ETH"), ("WINGS", "BTC"),
        ("RLC", "BTC"), ("GNO", "BTC"), ("GUP", "BTC"), ("LUN", "BTC"),
        ("GUP", "ETH"), ("RLC", "ETH"), ("LUN", "ETH"), ("GNO", "ETH"),
        ("APX", "BTC"), ("HMQ", "BTC"), ("HMQ", "ETH"), ("ANT", "BTC"),
        ("TRST", "ETH"), ("ANT", "ETH"), ("SC", "BTC"), ("BAT", "ETH"),
        ("BAT", "BTC"), ("ZEN", "BTC"), ("1ST", "BTC"), ("QRL", "BTC"),
        ("1ST", "ETH"), ("QRL", "ETH"), ("CRB", "BTC"), ("CRB", "ETH"),
        ("LGD", "ETH"), ("PTOY", "BTC"), ("PTOY", "ETH"), ("MYST", "BTC"),
        ("MYST", "ETH"), ("CFI", "BTC"), ("CFI", "ETH"), ("BNT", "BTC"),
        ("BNT", "ETH"), ("NMR", "BTC"), ("NMR", "ETH"), ("LTC", "ETH"),
        ("XRP", "ETH"), ("SNT", "BTC"), ("SNT", "ETH"), ("DCT", "BTC"),
        ("XEL", "BTC"), ("MCO", "BTC"), ("MCO", "ETH"), ("ADT", "BTC"),
        ("ADT", "ETH"), ("FUN", "BTC"), ("FUN", "ETH"), ("PAY", "BTC"),
        ("PAY", "ETH"), ("MTL", "BTC"), ("MTL", "ETH"), ("STORJ", "BTC"),
        ("STORJ", "ETH"), ("ADX", "BTC"), ("ADX", "ETH"), ("DASH", "ETH"),
        ("SC", "ETH"), ("ZEC", "ETH"), ("ZEC", "USDT"), ("LTC", "USDT"),
        ("ETC", "USDT"), ("XRP", "USDT"), ("OMG", "BTC"), ("OMG", "ETH"),
        ("CVC", "BTC"), ("CVC", "ETH"), ("PART", "BTC"), ("QTUM", "BTC"),
        ("QTUM", "ETH"), ("XMR", "ETH"), ("XEM", "ETH"), ("XLM", "ETH"),
        ("NEO", "ETH"), ("XMR", "USDT"), ("DASH", "USDT"), ("BCC", "ETH"),
        ("BCC", "USDT"), ("BCC", "BTC"), ("DNT", "BTC"), ("DNT", "ETH"),
        ("NEO", "USDT"), ("WAVES", "ETH"), ("STRAT", "ETH"), ("DGB", "ETH"),
        ("FCT", "ETH"), ("OMG", "USDT"), ("ADA", "BTC"), ("MANA", "BTC"),
        ("MANA", "ETH"), ("SALT", "BTC"), ("SALT", "ETH"), ("TIX", "BTC"),
        ("TIX", "ETH"), ("RCN", "BTC"), ("RCN", "ETH"), ("VIB", "BTC"),
        ("VIB", "ETH"), ("MER", "BTC"), ("POWR", "BTC"), ("POWR", "ETH"),
        ("BTG", "BTC"), ("BTG", "ETH"), ("BTG", "USDT"), ("ADA", "ETH"),
        ("ENG", "BTC"), ("ENG", "ETH"), ("ADA", "USDT"), ("XVG", "USDT"),
        ("NXT", "USDT"), ("UKG", "BTC"), ("UKG", "ETH"),
    )

    API = 'https://bittrex.com/api/v1.1'
    BOOK_URL = '%s/public/getorderbook?market={tickers[1]}-{tickers[0]}&type=both' % API
    TICKER_URL = '%s/public/getmarketsummary?market={tickers[1]}-{tickers[0]}' % API

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
