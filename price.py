#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
""" Module for price & conv features

TODO :
-full refactor !!
"""
import requests


class Switch(object):
    """ Custom switch class"""
    value = None

    def __new__(cls, value):
        cls.value = value
        return True


def case(*args):
    """ Custome case mimicked """
    return any((arg == Switch.value for arg in args))


def price(query):
    res = ''
    if len(query) >= 2:
        while Switch(query[1]):
            if case('polo'):
                query.remove('polo')
                res = poloniex(query)
                break
            if case('trex'):
                query.remove('trex')
                res = bittrex(query)
                break
            if case('poloniex'):
                query.remove('poloniex')
                res = poloniex(query)
                break
            if case('bittrex'):
                query.remove('bittrex')
                res = bittrex(query)
                break
            if case('p'):
                query.remove('p')
                res = poloniex(query)
                break
            if case('b'):
                query.remove('b')
                res = bittrex(query)
                break
            # market not provided
            res = lost(query)
            break

    return res


def conv(query):
    query.remove('conv')
    val_btc = btcrecup(0)
    val_btc_e = btcrecup(1)
    try:
        # if amount followed by currency
        float(query[0])
        final = polorecup(query[1], 0)

        if query[1].upper() == 'BTC':
            final = float(val_btc) * float(query[0])
            final2 = float(val_btc_e) * float(query[0])
            return '```{} {} valent {:.2f} $ ou {:.2f} €```'.format(
                query[0],
                query[1].upper(),
                final,
                final2
            )

        if final == 0:
            final = bittrecup(query[1], 0)
        if final != 0:
            final2 = (float(val_btc_e) * (float(final) / float(val_btc))) * float(query[0])
            final = float(final) * float(query[0])
            final = '```{} {} valent {:.2f} $ ou {:.2f} € ({:.4f} ฿)```'.format(
                query[0],
                query[1].upper(),
                final,
                final2,
                final / val_btc
            )
    except:
        # if currency followed by amount
        try:
            float(query[1])
        except:
            query[1] = 0

        if query[0].upper() == 'BTC':
            final = float(val_btc) * float(query[1])
            final2 = float(val_btc_e) * float(query[1])
            return '```{} {} valent {:.2f} $ ou {:.2f} €```'.format(
                query[1],
                query[0].upper(),
                final,
                final2
            )

        final = polorecup(query[0], 0)
        if final == 0:
            final = bittrecup(query[0], 0)

        if final != 0:
            final2 = (float(val_btc_e) * (float(final) / float(val_btc))) * float(query[1])
            final = float(final) * float(query[1])
            final = '```{} {} valent {:.2f} $ ou {:.2f} € ({:.4f} ฿)```'.format(
                query[1],
                query[0].upper(),
                final,
                final2,
                final/val_btc
            )

    return final


def bittrex(query):
    i = 0
    final = ['', '', '', '', '', '']
    query.remove('price')
    nb_case = len(query)
    offset = 0

    while nb_case > i:
        final[offset] = bittrecup(query[i], 1)
        if final[offset] != 0:
            offset += 1
        i = 1 + i

    return final


def poloniex(query):
    i = 0
    final = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    query.remove('price')
    nb_case = len(query)
    offset = 0

    while nb_case > i:
        final[offset] = polorecup(query[i], 1)
        if final[offset] != 0:
            offset += 1
        i = 1 + i

    return final


def finexrecup(currency, more):
    url = 'https://api.bitfinex.com/v1/pubticker/{}btc'.format(currency)
    val_btc = btcrecup(0)
    content = requests.get(url)
    data = content.json()

    if 'bid' in data:
        if more:
            return '```{}\t{} ฿  {:.2f}$ (Bitfinex)```'.format(
                currency.upper(),
                data['last_price'],
                float(data['last_price']) * val_btc
            )
        else:
            return float(data['last_price']) * val_btc
    else:
        return 0


def lost(query):
    i = 0
    final = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    query.remove('price')
    nb_case = len(query)

    while nb_case > i:
        final[i] = polorecup(query[i], 1)
        if final[i] == 0:
            final[i] = bittrecup(query[i], 1)
        if final[i] == 0:
            final[i] = finexrecup(query[i], 1)
        i = 1 + i

    return final


def polorecup(currency, more):
    market = 'BTC_' + currency.upper()
    val_btc = btcrecup(0)
    val_btc_e = btcrecup(1)

    if market == 'BTC_BTC':
        value = '```1 BTC vaut {} $ ou {} €```'.format(val_btc, val_btc_e)
        return value

    url = 'https://poloniex.com/public?command=returnTicker'
    content = requests.get(url)
    data = content.json()

    if market in data:
        if more:
            return '```{}\t{} ฿ ({:.2f} %) {:.2f}$ (Poloniex)```'.format(
                currency.upper(),
                data[market]['last'],
                float(data[market]['percentChange']) * 100,
                float(data[market]['last']) * val_btc
            )
        else:
            return float(data[market]['last']) * val_btc
    else:
        return 0


def bittrecup(currency, more):
    val_btc = btcrecup(0)
    url = 'https://bittrex.com/api/v1.1/public/getmarketsummary?market=btc-{}'.format(currency)
    content = requests.get(url)
    data = content.json()

    if data['success']:
        if more:
            percent1 = ((data['result'][0]['Last']) - (data['result'][0]['PrevDay']))
            percent2 = (percent1 / float(data['result'][0]['PrevDay'])) * 100

            return '```{}\t{} ฿ ({:.2f} %) {:.2f}$ (Bittrex)```'.format(
                currency.upper(),
                data['result'][0]['Last'],
                percent2,
                data['result'][0]['Last'] * val_btc
            )
        else:
            return data['result'][0]['Last'] * val_btc
    else:
        return 0


def btcrecup(euro):
    if euro:
        url = 'https://www.bitstamp.net/api/v2/ticker/btceur/'
    else:
        url = 'https://www.bitstamp.net/api/v2/ticker/btcusd/'

    content = requests.get(url)
    data = content.json()
    if 'last' in data:
        return float(data['last'])
    else:
        return 0
