#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Chart functionnality

This is where the chart is :
- created by querying the exchanges
- drawn using bokeh
- saved as a png file in order to be sent to discord

"""
import pandas as pd
import requests
import time
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d, PrintfTickFormatter
from bokeh.io import export_png


class Chart:
    """
    Book class

    We initialize the class with prefixed values to obtain a somewhat good looking drawing

    """

    def __init__(self):
        self.chart_params = {
            'title': '',
            'colors': {'up': 'Green', 'down': 'Red'},
            'size': {'height': 500, 'width': 750},
            'indicators': [
                {'name': 'ema', 'period': 12, 'color': '#EDFF86'},
                {'name': 'ema', 'period': 26, 'color': '#F4743B'}
            ],
            'tickFormat': '%1.8f'
        }

    @staticmethod
    def ema(df, n):
        """
        A simple EMA indicator to append to the chart

        :param df: OCHLV data
        :type: DataFrame
        :param n: Window
        :type n: int
        :return: OCHLV data + EMA Serie
        :rtype: DataFrame
        """
        price = df['close']
        price.fillna(method='ffill', inplace=True)
        price.fillna(method='bfill', inplace=True)
        ema = pd.Series(price.ewm(span=n, min_periods=n - 1).mean(), name='EMA_' + str(n))
        df = df.join(ema)
        return df

    def draw_chart(self, df):
        """
        The actual drawing method


        :param df: OCHLV data
        :type df: DataFrame
        :return: Drawn chart
        :rtype: Bokeh figure
        """
        # Computing indicators before triming data because of the window frame
        for i in self.chart_params['indicators']:
            if i['name'] is 'ema':
                df = self.ema(df, i['period'])
        # Keeping only most recent 48 ticks -> 24h
        df = df.tail(48)
        p = figure(
            x_axis_type='datetime',
            plot_width=self.chart_params['size']['width'],
            plot_height=self.chart_params['size']['height'],
            title=self.chart_params['title'])

        # Actual drawing of the chart
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
        p.y_range = Range1d(df['low'].min() * 0.995, df['high'].max() * 1.003)
        p.extra_y_ranges = {'foo': Range1d(start=-0, end=3 * df['volume'].max())}
        p.yaxis[0].formatter = PrintfTickFormatter(format=self.chart_params['tickFormat'])
        # Adding second axis for volume to the plot.
        p.add_layout(LinearAxis(y_range_name='foo'), 'right')
        p.grid[0].ticker.desired_num_ticks = 10
        p.axis.major_tick_line_color = 'whitesmoke'
        p.axis.minor_tick_line_color = 'whitesmoke'
        p.axis.axis_line_color = 'whitesmoke'
        p.yaxis[1].ticker.desired_num_ticks = 5
        p.xaxis.major_label_text_font_size = '10pt'
        p.yaxis[0].major_label_text_font_size = '10pt'
        p.axis.major_label_text_color = 'whitesmoke'
        p.axis.major_label_text_font = 'noto'
        p.yaxis[1].bounds = (0, df['volume'].max())
        inc = df['close'] > df['open']
        dec = df['open'] >= df['close']
        half_day_in_ms_width = 20 * 60 * 1000

        # volumes
        p.vbar(
            df.date[inc],
            half_day_in_ms_width,
            0,
            df.volume[inc],
            fill_color='green',
            line_color='#222222',
            y_range_name='foo',
            alpha=0.4
        )
        p.vbar(
            df.date[dec],
            half_day_in_ms_width,
            0,
            df.volume[dec],
            fill_color='red',
            line_color='#222222',
            y_range_name='foo',
            alpha=0.4
        )

        # candlesticks
        p.segment(df['date'], df['high'], df['date'], df['low'], color='white')
        p.vbar(
            df.date[inc],
            half_day_in_ms_width,
            df.open[inc],
            df.close[inc],
            fill_color='green',
            line_color='#222222'
        )
        p.vbar(
            df.date[dec],
            half_day_in_ms_width,
            df.open[dec],
            df.close[dec],
            fill_color='red',
            line_color='#222222'
        )
        
        for i in self.chart_params['indicators']:
            if i['name'] is 'ema':
                p.line(
                    df['date'],
                    df['EMA_' + str(i['period'])],
                    line_dash=(4, 4),
                    color=i['color'],
                    legend='EMA ' + str(i['period']),
                    line_width=2
                )

        p.legend.location = 'top_left'
        p.legend.label_text_font = 'noto'
        p.legend.label_text_color = 'whitesmoke'
        p.legend.background_fill_color = '#36393e'
        p.legend.background_fill_alpha = 0.7

        return p

    def chart(self, strcur):
        """
        The entrypoint for drawing order books

        This method is in charge of querying data from the exchanges & formatting it in order to be drawn
        :param strcur: desired currency
        :type strcur: Str
        :return: Image path
        :rtype: Str
        """

        cur = strcur.upper()
        end = round(time.time())
        # 48 hours of data, 30 min periods
        start = end - 2 * 86400
        if cur in ('BTC', 'XBT'):
            self.chart_params['title'] = 'BITFINEX USD-BTC'
            self.chart_params['tickFormat'] = '%f'
            url = 'https://api.bitfinex.com/v2/candles/trade:30m:tBTCUSD/hist'
            content = requests.get(url)
            data = content.json()
            df = pd.DataFrame.from_dict(data)
            df.rename(columns={2: 'close', 3: 'high', 4: 'low', 1: 'open', 0: 'date', 5: 'volume'}, inplace=True)
            # bitfinex needs reverse index
            df = df.iloc[::-1]
            df['date'] = pd.to_datetime(df['date'], unit='ms')
    
        else:
            # The exchange priority is Bitfinex > Poloniex > Bittrex
            self.chart_params['tickFormat'] = '%1.8f'
            url = 'https://api.bitfinex.com/v2/candles/trade:30m:t'+cur+'BTC/hist'
            content = requests.get(url)
            data = content.json()
            if len(data) is 0:
                self.chart_params['tickFormat'] = '%1.8f'
                url = 'https://poloniex.com/public?command=returnChartData&currencyPair=BTC_{}&start={}&end={}&period=1800'.format(cur, start, end)  # noqa
                content = requests.get(url)
                data = content.json()
                if 'error' in data:
                    url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=BTC-{}&tickInterval=thirtyMin&_={}'.format(cur, end)  # noqa
                    content = requests.get(url)
                    data = content.json()
                    if not data['success']:
                        print('error')
                        return ''
                    self.chart_params['title'] = 'BITTREX BTC-' + cur
                    df = pd.DataFrame.from_dict(data['result'])
                    df.rename(columns={'C': 'close', 'H': 'high', 'L': 'low', 'O': 'open', 'T': 'date', 'V': 'volume'},
                              inplace=True)
                    df['volume'] = df['volume'] * df['close']
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.tail(80)

                else:
                    self.chart_params['title'] = 'POLONIEX BTC-' + cur
                    df = pd.DataFrame.from_dict(data)
                    df['date'] = pd.to_datetime(df['date'], unit='s')
            else:
                self.chart_params['title'] = 'BITFINEX BTC-' + cur
                df = pd.DataFrame.from_dict(data)
                df.rename(columns={2: 'close', 3: 'high', 4: 'low', 1: 'open', 0: 'date', 5: 'volume'}, inplace=True)
                # bitfinex needs reverse index
                df = df.iloc[::-1]
                df['date'] = pd.to_datetime(df['date'], unit='ms')
                df['volume'] = df['volume'] * df['close']

        p = self.draw_chart(df)
        export_png(p, filename=cur + '_chart.png')
        return cur + '_chart.png'
