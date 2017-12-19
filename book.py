#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Book functionnality

This is where the order book is :
- created by querying the exchanges
- drawn using bokeh
- saved as a png file in order to be sent to discord

"""
import numpy as np
import pandas as pd
import requests
from bokeh.plotting import figure
from bokeh.models import Range1d, PrintfTickFormatter
from bokeh.io import export_png


class Book:
    """
    Book class

    We initialize the class with prefixed values to obtain a somewhat good looking drawing

    """

    def __init__(self):
        self.book_params = {
            'title': '',
            'colors': {'bid': 'Green', 'ask': 'Red'},
            'size': {'height': 500, 'width': 750},
            'depth': 100,
            'tickFormat': '%1.8f'
        }

    def draw_book(self, df):
        """
        The actual drawing method


        :param df: Ask & Bids with cumulated BTC amount
        :type df: DataFrame
        :return: Drawn order book
        :rtype: Bokeh figure
        """
        asks = df['ask'].dropna()
        bids = df['bid'].dropna()
        p = figure(plot_width=self.book_params['size']['width'],
                   plot_height=self.book_params['size']['height'],
                   title=self.book_params['title'] + '\t\tBid : %1.8f \tAsk : %1.8f\tSpread : %1.8f' %
                                                     (bids.index[-1], asks.index[0], asks.index[0] - bids.index[-1]))

        # Actual drawing of the order book
        p.toolbar.logo = None
        p.toolbar_location = None
        p.title.text_color = 'whitesmoke'
        p.title.text_font = 'noto'
        p.background_fill_color = '#36393e'
        p.border_fill_color = '#36393e'
        p.grid.grid_line_color = 'whitesmoke'
        p.grid.grid_line_alpha = 0.4
        p.grid.minor_grid_line_color = 'whitesmoke'
        p.grid.minor_grid_line_alpha = 0.2
        p.outline_line_color = 'whitesmoke'
        p.outline_line_alpha = 0.3
        p.xaxis.formatter = PrintfTickFormatter(format=self.book_params['tickFormat'])
        p.yaxis.formatter = PrintfTickFormatter(format='%f')
        p.axis.major_tick_line_color = 'whitesmoke'
        p.axis.minor_tick_line_color = 'whitesmoke'
        p.axis.axis_line_color = 'whitesmoke'
        p.axis.major_label_text_color = 'whitesmoke'
        p.axis.major_label_text_font = 'noto'
        p.axis.major_label_text_font_size = '10pt'
        p.x_range = Range1d(bids.index.min(), asks.index.max())
        p.y_range = Range1d(0, max(bids.max(), asks.max()))
        p.patch(np.append(np.array(asks.index), [np.array(asks.index).max(), np.array(asks.index).min()]),
                np.append(asks.values, [0, 0]), alpha=0.7,
                line_width=2, color=self.book_params['colors']['ask'])
        p.patch(np.append(np.array(bids.index), [np.array(bids.index).max(), np.array(bids.index).min()]),
                np.append(bids.values, [0, 0]), alpha=0.7,
                line_width=2, color=self.book_params['colors']['bid'])

        return p

    def book(self, str_cur):
        """
        The entrypoint for drawing order books

        This method is in charge of querying data from the exchanges & formatting it in order to be drawn
        :param str_cur: desired currency
        :type str_cur: Str
        :return: Image path
        :rtype: Str
        """

        cur = str_cur.upper()
        # Currency is BTC
        if cur in ('BTC', 'XBT'):
            self.book_params['title'] = 'BITFINEX USD-BTC'
            self.book_params['tickFormat'] = '%f'
            url = 'https://api.bitfinex.com/v2/book/tBTCUSD/P0/?len={}'.format(self.book_params['depth'])
            content = requests.get(url)
            data = content.json()
            df = pd.DataFrame.from_dict(data)
            df.rename(columns={0: 'price', 1: 'count', 2: 'amount'}, inplace=True)
            df_asks = df[['price', 'amount']][df['amount'] < 0]
            df_asks = df_asks.abs()
            df_bids = df[['price', 'amount']][df['amount'] > 0]
            df_asks.rename(columns={'amount': 'ask'}, inplace=True)
            df_bids.rename(columns={'amount': 'bid'}, inplace=True)
        else:
            # The exchange priority is Bitfinex > Poloniex > Bittrex
            self.book_params['tickFormat'] = '%1.8f'
            url = 'https://api.bitfinex.com/v2/book/t{}BTC/P0/?len={}'.format(
                cur,
                self.book_params['depth']
            )
            content = requests.get(url)
            data = content.json()
            if 'error' in data:
                url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_{}&depth={}'.format(
                    cur,
                    self.book_params['depth']
                )
                content = requests.get(url)
                data = content.json()
                if 'error' in data:
                    url = 'https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-{}&type=both&depth=100'.format(
                        cur
                    )
                    content = requests.get(url)
                    data = content.json()
                    if not data['success']:
                        print('error')
                        return ''
                    self.book_params['title'] = 'BITTREX BTC-' + cur
                    data = data['result']
                    df_asks = pd.DataFrame.from_dict(data['sell'])
                    df_asks.rename(columns={'Rate': 'price', 'Quantity': 'ask'}, inplace=True)
                    df_bids = pd.DataFrame.from_dict(data['buy'])
                    df_bids.rename(columns={'Rate': 'price', 'Quantity': 'bid'}, inplace=True)
                    # Cuz bittrex api is shitty
                    df_bids = df_bids.head(self.book_params['depth'])
                    df_asks = df_asks.head(self.book_params['depth'])

                else:
                    self.book_params['title'] = 'POLONIEX BTC-' + cur
                    df_asks = pd.DataFrame.from_dict(data['asks'])
                    df_asks.rename(columns={0: 'price', 1: 'ask'}, inplace=True)
                    df_bids = pd.DataFrame.from_dict(data['bids'])
                    df_bids.rename(columns={0: 'price', 1: 'bid'}, inplace=True)
            else:
                self.book_params['title'] = 'BITFINEX BTC-' + cur
                df = pd.DataFrame.from_dict(data)
                df.rename(columns={0: 'price', 1: 'count', 2: 'amount'}, inplace=True)
                df_asks = df[['price', 'amount']][df['amount'] < 0]
                df_asks = df_asks.abs()
                df_bids = df[['price', 'amount']][df['amount'] > 0]
                df_asks.rename(columns={'amount': 'ask'}, inplace=True)
                df_bids.rename(columns={'amount': 'bid'}, inplace=True)

        df_asks['ask'] = df_asks['ask'] * df_asks['price'].astype(float)
        df_bids['bid'] = df_bids['bid'] * df_bids['price'].astype(float)
        df_asks.set_index(['price'], inplace=True)
        df_bids.set_index('price', inplace=True)
        df_asks = df_asks.cumsum()
        df_bids = df_bids.cumsum()
        df = df_asks.join(df_bids, how='outer')
        df.index = df.index.astype(float)

        p = self.draw_book(df)
        export_png(p, filename=cur + '_book.png')
        return cur + '_book.png'
