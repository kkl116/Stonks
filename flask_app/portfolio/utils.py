from flask_table import Col
from ..utils.table_helpers import (Col_, TickerItem, 
                                Table_, new_item_json)
from flask_login import current_user 
import stockquotes
from ..models import PortfolioItem, Portfolio
import numpy as np 
import yfinance as yf
from flask import url_for, jsonify
from flask_app import db

def get_portfolio_items(arg_dict, mode="all"):
    """pass query params to get porfolio items
    - if you want to query items using user, pass {'user': current_user},
    - mode indicates which items to get -- all or first usually"""
    if 'user' in arg_dict.keys():
        arg_dict.update({'portfolio': get_user_portfolio(arg_dict['user'])})
        del arg_dict['user']
    items = PortfolioItem.query.filter_by(**arg_dict).order_by(PortfolioItem.ticker_name.desc())
    return getattr(items, mode)()

def get_user_portfolio(user):
    return Portfolio.query.filter_by(user=user).first()

def get_ticker_currency(ticker_name):
    ticker = yf.Ticker(ticker_name)
    return ticker.info['currency'].strip().upper()

def add_update_portfolio(add_form, ticker_name):
    """given ticker_name and add_form, queries database to see if ticker has been added - 
    if already added, updates entry, or else creates an entry for update"""

    def get_new_purchase_price(item, add_form):
        """function to update purchase price -- similiar to """
        quantities = [float(i) for i in [add_form.quantity.data, item.quantity]]
        prices = [float(i) for i in [add_form.purchase_price.data, item.purchase_price]]
        return np.average(prices, weights=quantities)

    try:
        print('updating')
        item = get_portfolio_items({'user': current_user, 'ticker_name': ticker_name})[0]
        #update quantity and average price 
        item.purchase_price = get_new_purchase_price(item, add_form)
        item.quantity = str(float(item.quantity) + float(add_form.quantity.data))
    except:
        print('adding')
        item = PortfolioItem(portfolio=get_user_portfolio(current_user),
        ticker_name=ticker_name, purchase_price=add_form.purchase_price.data,
        quantity=add_form.quantity.data, currency=get_ticker_currency(ticker_name))
        db.session.add(item)
    db.session.commit()

    return item

class TickerItem_Portfolio(TickerItem):
    """object to pass to portfolio table -- 
    returns the total position across all purchases of the ticker"""
    def __init__(self, *args, **kwargs):
        super(TickerItem_Portfolio, self).__init__(*args, **kwargs)
        self.n_places = 2
        self.item = self.empty_or_attr(attr=[{'user': current_user, 'ticker_name': self.ticker}, 'first'], func=get_portfolio_items)
        self.purchase_price = self.empty_or_attr(attr=[], func=self.get_purchase_price)
        self.gain = self.empty_or_attr(attr=[self.current_price, self.purchase_price], func=self.get_gain)
        self.percent_gain = self.empty_or_attr(attr=[self.gain, self.purchase_price], func=self.get_percent_gain)
        self.quantity = self.empty_or_attr(attr=[], func=self.get_quantity)
        self.arrow_icon = self.empty_or_attr(attr=[], func=self.arrow_icon)
        self.delete = self.empty_or_attr(attr=[url_for('portfolio.delete')], func=self.delete_btn)
        #have a sell button? I dunno
        try:
            self.update_html_attrs(self.color_style())
        except Exception as e:
            print(e)
            
    def arrow_icon(self):
        """give an green up arrow or red down arrow depending on status"""
        if self.gain > 0:
            return '<i class="fas fa-arrow-alt-circle-up" style="color:#027E4A;"></i>'
        elif self.gain < 0:
            return '<i class="fas fa-arrow-alt-circle-down" style="color:#EF3125;"></i>'
        elif self.gain == 0:
            return '<i class="fas fa-dot-circle"></i>'

    def get_purchase_price(self):
        return round(float(self.item.purchase_price), self.n_places)

    def get_quantity(self):
        return round(float(self.item.quantity), self.n_places)

    def get_gain(self, current_price, purchase_price):
        current_price, purchase_price = [float(p) for p in [current_price, purchase_price]]
        return round(current_price - purchase_price, self.n_places)
    
    def get_percent_gain(self, gain, purchase_price):
        gain, purchase_price = [float(p) for p in[gain, purchase_price]]
        return round((gain/purchase_price)*100, self.n_places)

    def color_style(self):
        if self.gain != 0:
            if self.gain > 0:
                color = self.green_hex
            elif self.gain < 0:
                color = self.red_hex
        return {'style': f"color: {color} !important;"}

class PortfolioTable(Table_):
    def __init__(self, *args, **kwargs):
        super(PortfolioTable, self).__init__(*args, **kwargs)
    
    classes = ['table', 'table-hover', 'table-sm', 'table-collapse']
    arrow_icon = Col_('ICON', hide_header=True)
    ticker_link = Col_('TICKER')
    purchase_price = Col('PURCHASE PRICE')
    quantity = Col('QUANTITY')
    current_price = Col('CURRENT PRICE')
    gain = Col_('GAIN', use_item_attrs=True)
    percent_gain = Col_('PERCENT GAIN', use_item_attrs=True)
    delete = Col_('DELETE', hide_header=True)
    table_id = 'portfolio-table'


