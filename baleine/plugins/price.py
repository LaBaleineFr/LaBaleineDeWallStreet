import asyncio
from baleine import command, exchange, util


class Price(command.Command):
    """ Bot command that shows the price of some security """
    name = 'price'

    errors = {
        'usage': '{name} <ticker>[/<ticker>] [exchange]',
        'unknown_exchange': 'je ne connais pas l\'exchange "{name}".',
        'unknown_pair': 'je ne connais pas la paire "{pair[0]}{pair[1]}".',
        'pair_not_found': 'je n\'ai pas trouvé le prix sur cet exchange.',
    }

    async def execute(self, message, args):
        if len(args) < 1 or len(args) > 2:
            await self.error('usage', name=self.name)
            return

        # Mark ourselves as typing
        asyncio.ensure_future(self.output.notify(), loop=self.client.loop)

        # Try to guess the correct pair
        symbol = args[0].upper()
        if '/' in symbol:
            tickers = tuple(symbol.split('/', 1))
        else:
            if symbol in ('BTC', 'XBT'):
                tickers = ('BTC', 'USD')
            else:
                tickers = (symbol, 'BTC')

        # Get exchange from pair or the one given on command
        if len(args) == 2:
            # Exchange name was given explicitly
            try:
                xchg = exchange.get(args[1].lower())
            except KeyError:
                await self.error('unknown_exchange', name=args[1])
                return
        else:
            # Exchange name not given, find the best match
            try:
                xchg = await exchange.pair(tickers)
            except ValueError:
                await self.error('unknown_pair', pair=tickers)
                return

        # Get prices
        try:
            prices = await xchg.get_prices(tickers)
        except IOError as exc:
            await self.error('pair_not_found')
            return

        await self.send(
            '{exchange} {tickers[0]}/{tickers[1]}: **{last}** [{change:+.2%}], {volume} vol'.format(
                exchange=xchg.name.capitalize(),
                tickers=tickers,
                last=util.format_price(prices.last, tickers[1], hide_ticker=True),
                change=prices.change,
                volume=util.format_price(prices.volume, tickers[0], hide_ticker=True)
                       if prices.volume > 0 else '-',
            )
        )
