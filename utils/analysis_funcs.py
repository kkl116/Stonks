import math 
import numpy as np 
import pandas as pd 
import stockquotes
import yfinance as yf
from forex_python.converter import CurrencyRates

def market_cap(ticker_name):
    """Numbers from investopedia 2021-03-26
    - Mega: largest basically, represents leader of a sector or a market.
    - Large: p big p big
    Mega and large = blue chip stocks, considered relatively stable and secure.
    - Mid: Growth stocks represent a significant portion of mid-caps. Some 
    may not be industry leaders, but may be on way to become one.
    - Small: majority are young companies with promising growth, but also few established businesses which
    may have lost value in recent times. 
    - Micro: mainly penny stocks, e.g. lesser known pharma with no marketable product and 
    working on developing a drug for an incurable disease.
    - Nano: high-risk high-reward. Typically pink sheets stuff.
    
    I suppose it's a quick gauge of risk vs. reward, although obviously not a one-fits-all metric"""
    ticker = yf.Ticker(ticker_name)
    cap = ticker.get_info()['marketCap']
    #convert currency if not usd
    currency = ticker.get_info()['currency']
    if currency != 'USD':
        cap = c.get_rates(currency, 'USD', cap)
    category = None
    if cap < 50000000:
        category = 'nano'
    elif  50000000 <= cap < 300000000:
        category = 'micro'
    elif 300000000 <= cap < 2000000000:
        category = 'small'
    elif 2000000000 <= cap < 10000000000:
        category = 'mid'
    elif 10000000000 <= cap < 200000000000:
        category = 'large'
    elif 200000000000 <= cap:
        category = 'mega'
    return cap, category

