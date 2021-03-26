import json 
import time
import random
import stockquotes 
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from get_all_tickers import get_tickers

def get_live_quotes(ticker_name, test=False, interval = 10):
    while True:
        "expects yahoo finance stock symbols"
        stock = stockquotes.Stock(ticker_name)
        if test:
            value = random.random()
        else:
            value = stock.current_price
        #not getting time from here b/c js time seems more compatible... so in reality it's 1-2s delay but doesnt really matter
        json_data = json.dumps(
            {#'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'value': value})
        yield f"data:{json_data}\n\n"
        time.sleep(interval)

def get_previous_close(ticker_name, test=False):
    "expects yahoo finance stock symbols"
    stock = stockquotes.Stock(ticker_name)
    if test:
        value = 0.5
    else:
        value = stock.historical[0]['close']

    return value

def check_ticker_exists(ticker):
    url = f'https://uk.finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'
    page = requests.get(url)
    if page.url == url:
        return True
    else:
        return False

