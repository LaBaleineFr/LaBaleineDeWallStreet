import asyncio
from baleine import command, exchange, util


class Convert(command.Command):
    """ Bot command that converts some amount from a coin into another """
    name = 'conv'

    errors = {
        'usage': '{name} <montant> <ticker> [<ticker>]',
        'invalid_amount': 'montant {amount} non reconnu',
        'unknown_coin': 'je ne connais pas le coin « {ticker} »',
        'cannot_convert': 'je ne sais pas convertir « {tickers[0]} » en « {tickers[1]} »',
    }

    async def execute(self, message, args):
        if len(args) == 0:
            await self.error('usage', name=self.name)
            return

        # Parse value
        try:
            value = float(args[0])
        except ValueError:
            await self.error('invalid_amount', amount=args[0])
            return

        # Mark ourselves as typing
        asyncio.ensure_future(self.output.notify(), loop=self.client.loop)

        if len(args) == 2:
            # Only one coin name was given, convert to EUR and USD
            ticker = args[1].upper()

            try:
                result = await asyncio.gather(
                    self.do_convert(value, (ticker, 'USD')),
                    self.do_convert(value, (ticker, 'EUR')),
                    loop=self.client.loop,
                )
            except ValueError:
                await self.error('unknown_coin', ticker=ticker)
            else:
                await self.send(
                    '{value} valent {usd}$ ou {eur}€'.format(
                    value=util.format_price(value, ticker),
                    usd=util.format_price(result[0], 'USD', hide_ticker=True),
                    eur=util.format_price(result[1], 'EUR', hide_ticker=True),
                ))

        elif len(args) == 3:
            # Two coin names, find a way to convert between them
            tickers = (args[1].upper(), args[2].upper())

            try:
                result = await self.do_convert(value, tickers)
            except ValueError:
                await self.error('cannot_convert', tickers=tickers)
            else:
                await self.send(
                    '{value} valent {result}'.format(
                    value=util.format_price(value, tickers[0]),
                    result=util.format_price(result, tickers[1]),
                ))
        else:
            await self.error('usage', name=self.name)

    async def do_convert(self, value, tickers):
        try:
            # If we know an exchange that can convert, great, use it
            invert, xchg = False, await exchange.pair(tickers)
        except ValueError:
            # See if we know an exchange that can do the conversion backwards
            invert, tickers = True, (tickers[1], tickers[0])
            try:
                xchg = await exchange.pair(tickers)
            except ValueError:
                # No direct conversion exist, try to go through bitcoin
                if 'BTC' in tickers:
                    raise
                btc = await self.do_convert(value, ('BTC', tickers[0]))
                result = await self.do_convert(btc, (tickers[1], 'BTC'))
                return result

        prices = await xchg.get_prices(tickers)
        return value/prices.last if invert else value*prices.last
