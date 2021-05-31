from flask_table import Col
from ..utils.table_helpers import (Col_, TickerItem, 
                                Table_, new_item_json)
from flask_login import current_user 
import stockquotes
from ..models import PortfolioItem
import numpy as np 
import yfinance as yf
from flask import url_for, jsonify
from flask_app import db
from currency_symbols import CurrencySymbols
import requests, json

def get_exchange_rate(from_currency, to_currency, apikey='761WW05Z48CV56CK'):
    """Get fx rate from alphavantage free api:)"""
    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={apikey}'
    r = requests.get(url)
    r = r.json()['Realtime Currency Exchange Rate']
    rate = float(r['5. Exchange Rate'])
    #here adjust for fact that GBp indicates trading in pence
    if from_currency == 'GBp':
        rate /= 100
    elif to_currency == 'GBp':
        rate *= 100
    return rate

def get_unique_ticker_names(query_items):
    """just returns unique ticker_names from list of queries"""
    ticker_names = [q.ticker_name for q in query_items]
    return list(set(ticker_names))

def get_ticker_currency(ticker_name):
    ticker = yf.Ticker(ticker_name)
    return ticker.info['currency']

def get_summary_row(query_items):
    def consolidate_items(active_items):
        """consolidate query items into a dict
        ticker_name: [avg_purchase_price, total_quantity, currency]"""
        ticker_names = list(set([item.ticker_name for item in active_items]))
        avg_prices = []
        total_quantities = []
        currencies = []
        for name in ticker_names:
            ticker_items = [item for item in active_items if item.ticker_name == name]
            prices = [float(item.purchase_price) for item in ticker_items]
            quantitites = [float(item.quantity) for item in ticker_items]
            avg_price = np.average(prices, weights=quantitites)
            avg_prices.append(avg_price)
            total_quantities.append(sum(quantitites))
            currencies.append(ticker_items[0].currency)
        return {n:[p,q,c] for n,p,q,c in zip(ticker_names, avg_prices, total_quantities, currencies)}
    #initialize an empty item 
    item = TickerItem_Portfolio('empty')
    item.ticker_link = 'TOTAL'
    active_items = consolidate_items([item for item in query_items if item.status != "SOLD"])
    original_value = 0
    market_value = 0
    gain = 0
    user_currency = current_user.currency
    user_currency_symbol = CurrencySymbols.get_symbol(user_currency)
    for ticker_name in active_items:
        ticker_props = active_items[ticker_name]
        current_price = stockquotes.Stock(ticker_name).current_price
        if user_currency == ticker_props[2]:
            exch_rate = 1
        else:
            exch_rate = get_exchange_rate(ticker_props[2], user_currency)
        
        current_value = current_price * ticker_props[1] * exch_rate
        purchase_value = ticker_props[0] * ticker_props[1] * exch_rate

        market_value += current_value 
        gain += (current_value - purchase_value) 
        original_value += purchase_value

    market_value, gain = [round(v, 2) for v in [market_value, gain]]
    percent_gain = round((gain/original_value)*100, 2)

    item.market_value = user_currency_symbol + str(market_value)
    item.gain = user_currency_symbol + str(gain)
    item.percent_gain = percent_gain
    return item
    
    

#edit tickeritem portfolio so that it consolidates all the purchase orders
class TickerItem_Portfolio(TickerItem):
    """object to pass to portfolio table -- 
    returns the total position across all purchases of the ticker"""
    def __init__(self, *args, **kwargs):
        super(TickerItem_Portfolio, self).__init__(*args, **kwargs)
        self.n_places = 2
        self.items = self.empty_or_attr(attr=[{'user': current_user, 'ticker_name': self.ticker}, 'all'], func=self.get_portfolio_items)
        #filter out items that have status SOLD
        self.items = [item for item in self.items if item.status != 'SOLD']
        self.purchase_price = self.empty_or_attr(attr=[], func=self.get_purchase_price)
        self.gain = self.empty_or_attr(attr=[], func=self.get_gain)
        self.percent_gain = self.empty_or_attr(attr=[], func=self.get_percent_gain)
        self.quantity = self.empty_or_attr(attr=[], func=self.get_quantity)
        self.market_value = self.empty_or_attr(attr=[], func=self.get_market_value)
        self.arrow_icon = self.empty_or_attr(attr=[], func=self.arrow_icon)
        self.delete = self.empty_or_attr(attr=[url_for('portfolio.delete')], func=self.delete_btn)
        #have a sell button? I dunno
        try:
            self.update_html_attrs(self.color_style())
        except Exception as e:
            print(e)
            
    def get_purchase_price(self):
        quantities = [float(item.quantity) for item in self.items]
        prices = [float(item.purchase_price) for item in self.items]
        price = np.average(prices, weights=quantities)
        return round(price, self.n_places)

    def get_quantity(self):
        return round(sum([float(item.quantity) for item in self.items]), self.n_places)

    def get_gain(self):
        return round(self.current_price - self.purchase_price, self.n_places)
    
    def get_percent_gain(self):
        return round((self.gain/self.purchase_price)*100, self.n_places)

    @staticmethod
    def get_portfolio_items(arg_dict, mode="all"):
        """pass query params to get porfolio items
        - if you want to query items using user, pass {'user': current_user},
        - mode indicates which items to get -- all or first usually
        - unique indicates whether to only return unique instances or not"""
        items = PortfolioItem.query.filter_by(**arg_dict).order_by(PortfolioItem.ticker_name.desc())
        return getattr(items, mode)()

    def get_market_value(self):
        currency = self.items[0].currency
        value = self.current_price * self.quantity
        if currency == 'GBp':
            value /= 100
        value = round(value, self.n_places)

        symbol = CurrencySymbols.get_symbol(currency.upper())
        return symbol + str(value)

    def color_style(self):
        if self.gain != 0:
            if self.gain > 0:
                color = self.green_hex
            elif self.gain < 0:
                color = self.red_hex
        return {'style': f"color: {color} !important;"}

    def arrow_icon(self):
        """give an green up arrow or red down arrow depending on status"""
        if self.gain > 0:
            return '<i class="fas fa-arrow-alt-circle-up" style="color:#027E4A;"></i>'
        elif self.gain < 0:
            return '<i class="fas fa-arrow-alt-circle-down" style="color:#EF3125;"></i>'
        elif self.gain == 0:
            return '<i class="fas fa-dot-circle"></i>'

class PortfolioTable(Table_):
    def __init__(self, *args, **kwargs):
        super(PortfolioTable, self).__init__(*args, **kwargs)
    
    classes = ['table', 'table-hover', 'table-sm', 'table-collapse']
    arrow_icon = Col_('ICON', hide_header=True)
    ticker_link = Col_('TICKER')
    purchase_price = Col('PURCHASE PRICE')
    quantity = Col('QUANTITY')
    current_price = Col('CURRENT PRICE')
    market_value = Col('MARKET VALUE')
    gain = Col_('GAIN', use_item_attrs=True)
    percent_gain = Col_('PERCENT GAIN', use_item_attrs=True)
    delete = Col_('DELETE', hide_header=True)
    table_id = 'portfolio-table'


