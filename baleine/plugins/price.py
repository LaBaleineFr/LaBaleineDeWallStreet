import asyncio
from baleine import command, exchange, util


class Price(command.Command):
    name = 'price'

    async def send_help(self):
        await self.error('%s <ticker> [<ticker>]' % self.name)

    async def execute(self, message, args):
        if len(args) < 1 or len(args) > 2:
            await self.send_help()
            return

        asyncio.ensure_future(self.output.notify(), loop=self.client.loop)

        symbol = args[0].upper()
        if len(symbol) > 3 and symbol.endswith(('BTC', 'XBT', 'ETH', 'USD', 'EUR')):
            tickers = (symbol[:-3], symbol[-3:])
        else:
            if symbol in ('BTC', 'XBT'):
                tickers = ('BTC', 'USD')
            else:
                tickers = (symbol, 'BTC')

        # Get exchange from pair or the one given on command
        if len(args) == 2:
            try:
                xchg = exchange.get(args[1].lower())
            except KeyError:
                await self.error('je ne connais pas l\'exchange "%s".' % args[1])
                return
        else:
            try:
                xchg = await exchange.pair(tickers)
            except ValueError:
                await self.error('je ne connais pas la paire "%s%s".' % tickers)
                return

        # Get prices
        try:
            prices = await xchg.get_prices(tickers)
        except IOError as exc:
            await self.error('je n\'ai pas trouvé le prix sur cet exchange.')
            return

        await self.send(
            '{exchange} {tickers[0]}/{tickers[1]}: **{last}** [{change:+.2%}], {volume} vol'.format(
                exchange=xchg.name.capitalize(),
                tickers=tickers,
                last=util.format_price(prices.last, tickers[1], hide_ticker=True),
                change=prices.change,
                volume=util.format_price(prices.volume, tickers[0], hide_ticker=True),
            )
        )
