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
                    y=hist['Volume']),
                    row=1, col=1)
    
    fig.update_layout({'paper_bgcolor': 'rgb(248, 249, 252)',
    'showlegend': False, 'hovermode': 'x unified'})
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return fig_json


def check_ticker_exists(ticker):
    url = f'https://uk.finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'
    page = requests.get(url)
    if page.url == url:
        return True
    else:
        return False

