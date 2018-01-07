import asyncio
from baleine import command, exchange, util


class Convert(command.Command):
    command = ('conv', 'convert')


    @asyncio.coroutine
    def send_help(self, client, message):
        yield from client.send_message(
            message.channel,
            '%s <montant> <ticker> [<ticker>]' % self.command[0],
        )

    @asyncio.coroutine
    def execute(self, client, message, args):
        if len(args) == 0:
            send_help(client, message)
            return
        try:
            value = float(args[0])
        except ValueError:
            yield from client.send_message(message.channel, '%s: montant %r non reconnu'
                                           % (message.author.mention, args[0]))
            return


        if len(args) == 2:
            ticker = args[1].upper()

            try:
                usdresult = yield from self.do_convert(value, (ticker, 'USD'))
                eurresult = yield from self.do_convert(value, (ticker, 'EUR'))
            except ValueError:
                yield from client.send_message(message.channel,
                    '{user}: je ne connais pas le coin "{ticker}"'.format(
                    user=message.author.mention,
                    ticker=ticker,
                ))
            else:
                yield from client.send_message(message.channel,
                    '{user}: {value} valent {usd}$ ou {eur}€'.format(
                    user=message.author.mention,
                    value=util.format_price(value, ticker),
                    usd=util.format_price(usdresult, 'USD', hide_ticker=True),
                    eur=util.format_price(eurresult, 'EUR', hide_ticker=True),
                ))

        elif len(args) == 3:
            tickers = (args[1].upper(), args[2].upper())

            try:
                result = yield from self.do_convert(value, tickers)
            except ValueError:
                yield from client.send_message(message.channel,
                    '{user}: je ne sais pas convertir "{tickers[0]}" en "{tickers[1]}"'.format(
                    user=message.author.mention,
                    tickers=tickers,
                ))
            else:
                yield from client.send_message(message.channel,
                    '{user}: {value} valent {result}'.format(
                    user=message.author.mention,
                    value=util.format_price(value, tickers[0]),
                    result=util.format_price(result, tickers[1]),
                ))
        else:
            yield from send_help(client, message)

    @asyncio.coroutine
    def do_convert(self, value, tickers):
        try:
            invert, xchg = False, exchange.pair(tickers)
        except ValueError:
            invert, tickers = True, (tickers[1], tickers[0])
            try:
                xchg = exchange.pair(tickers)
            except ValueError:
                if 'BTC' in tickers:
                    raise
                btc = yield from self.do_convert(value, ('BTC', tickers[0]))
                result = yield from self.do_convert(btc, (tickers[1], 'BTC'))
                return result

        prices = yield from xchg.get_prices(tickers)
        return value/prices.last if invert else value*prices.last

