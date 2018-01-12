import asyncio
from baleine import command, exchange, util


class Convert(command.Command):
    name = 'conv'

    async def send_help(self):
        await self.error('%s <montant> <ticker> [<ticker>]' % self.name)

    async def execute(self, message, args):
        if len(args) == 0:
            await self.send_help()
            return
        try:
            value = float(args[0])
        except ValueError:
            await self.error('montant %r non reconnu' % args[0])
            return


        if len(args) == 2:
            ticker = args[1].upper()

            try:
                usdresult = await self.do_convert(value, (ticker, 'USD'))
                eurresult = await self.do_convert(value, (ticker, 'EUR'))
            except ValueError:
                await self.error(
                    'je ne connais pas le coin "{ticker}"'.format(
                    ticker=ticker,
                ))
            else:
                await self.send(
                    '{value} valent {usd}$ ou {eur}€'.format(
                    value=util.format_price(value, ticker),
                    usd=util.format_price(usdresult, 'USD', hide_ticker=True),
                    eur=util.format_price(eurresult, 'EUR', hide_ticker=True),
                ))

        elif len(args) == 3:
            tickers = (args[1].upper(), args[2].upper())

            try:
                result = await self.do_convert(value, tickers)
            except ValueError:
                await self.error(
                    'je ne sais pas convertir "{tickers[0]}" en "{tickers[1]}"'.format(
                    tickers=tickers,
                ))
            else:
                await self.send(
                    '{value} valent {result}'.format(
                    value=util.format_price(value, tickers[0]),
                    result=util.format_price(result, tickers[1]),
                ))
        else:
            await self.send_help()

    async def do_convert(self, value, tickers):
        try:
            invert, xchg = False, exchange.pair(tickers)
        except ValueError:
            invert, tickers = True, (tickers[1], tickers[0])
            try:
                xchg = exchange.pair(tickers)
            except ValueError:
                if 'BTC' in tickers:
                    raise
                btc = await self.do_convert(value, ('BTC', tickers[0]))
                result = await self.do_convert(btc, (tickers[1], 'BTC'))
                return result

        prices = await xchg.get_prices(tickers)
        return value/prices.last if invert else value*prices.last
