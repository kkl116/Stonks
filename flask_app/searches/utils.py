import json 
import time
import random
import stockquotes 
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd 

#Remember to update yfinance package if any errors.

fig_default_layouts = {'paper_bgcolor': 'rgb(248, 249, 252)',
    'showlegend': False, 'hovermode': 'x unified'}

def get_hist_vol_json(ticker_name, testing=False, period="max", col="Close"):
    """gets price chart json data here that could be passed into html route"""
    ticker = yf.Ticker(ticker_name)
    hist = ticker.history(period=period)
    hist['Date'] = hist.index
    fig = make_subplots(rows=2, cols=1,
    shared_xaxes=True, subplot_titles=("Volume", "History"))
    fig.append_trace(go.Ohlc(
                    name="History",
                    x=hist['Date'],
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close']),
                    row=2, col=1)

    fig.append_trace(go.Line(
                    name="Volume",
                    x=hist['Date'],
                    y=hist['Volume'],
                    line=dict(color="royalblue")),
                    row=1, col=1)
    
    fig.update_layout(fig_default_layouts)
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json

def get_dropdown_items():
    items = list(dir(yf.Ticker))
    ignore = ['__', '_', 'get', 'isin', 'history', 'info', 'balancesheet', 'option_chain']
    items = [i for i in items if not any(i.startswith(string) for string in ignore)]
    display_string = [format_attr_string(i) for i in items]

    dropdowns = dict(zip(display_string, items))
    return dropdowns

def check_ticker_exists(ticker):
    url = f'https://uk.finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'
    page = requests.get(url)
    if page.url == url:
        return True
    else:
        return False

def format_attr_string(string):
    split = string.split('_')
    if len(split) == 1:
        return split[0].title()
    elif len(split) > 1:
        return ' '.join([s.title() for s in split])


def get_chart_json(ticker, item):
    """for each dropdown item chart can decide here what kind of chart to present...
    for now just do all tables -- """

    ticker = yf.Ticker(ticker)
    data = getattr(ticker, item)
    #need to deal with different datas here - some are tuples (dates), some are series (single columns), some are dfs
    #put df's index as a column
    if type(data) == pd.core.series.Series:
        df = data.to_frame()
    elif type(data) == tuple:
        df = pd.DataFrame(data)
    elif type(data) == pd.core.frame.DataFrame:
        df = data

    try:
        df.insert(0, format_attr_string(item), df.index)
    except Exception as e:
        print(e)

    df.fillna('-')
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(df.columns),
            fill_color="paleturquoise",
            align="left"),

            cells=dict(values=[df[col] for col in df.columns],
            fill_color='bisque',
            align='left'))
        ])

    fig.update_layout(fig_default_layouts)
    fig.update_layout(title_text=format_attr_string(item), title_x=0.5)
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json


