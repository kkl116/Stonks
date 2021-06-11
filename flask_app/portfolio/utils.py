from flask_table import Col
from ..utils.table_helpers import (Col_, TickerItem, 
                                Table_)
from flask_login import current_user 
from ..models import PortfolioItem, ExchangeRate
import numpy as np 
import yfinance as yf
from flask import url_for, jsonify
from flask_app import db
from currency_symbols import CurrencySymbols
import requests, json
import stockquotes
from flask_app import testing
from datetime import datetime

def query_exchange_rate(from_currency, to_currency):
    """basically check the database to see if there is this entry, if not then get it from api
    - rates are updated once a day"""
    query = ExchangeRate.query.filter_by(from_currency=from_currency, to_currency=to_currency).first()
    if query:
        #check if it has been updated today 
        if query.date_updated == str(datetime.today().date()):
            print('rate up to date')
            return float(query.rate)
        else:
            rate = get_exchange_rate(from_currency, to_currency)
            query.rate = str(rate)
            query.date_updated = str(datetime.today().date())
            #update reverse entry as well 
            reverse = ExchangeRate.query.filter_by(from_currency=to_currency, to_currency=from_currency).first()
            reverse.rate = str(1/rate)
            reverse.date_updated = str(datetime.today().date())
            db.session.commit()
            print('rate updated at: ', query.date_updated)
            return rate
    else:
        #query does not exist 
        rate = get_exchange_rate(from_currency, to_currency)
        new_entry = ExchangeRate(from_currency=from_currency, to_currency=to_currency, rate=str(rate))
        new_entry_reverse = ExchangeRate(from_currency=to_currency, to_currency=from_currency, rate=str(1/rate))
        db.session.add_all([new_entry, new_entry_reverse])
        db.session.commit()
        print(new_entry)
        return rate

def get_exchange_rate(from_currency, to_currency, apikey='761WW05Z48CV56CK', testing=False):
    if not testing:
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
    else:
        rate = 1
    return rate

def get_unique_ticker_names(query_items):
    """just returns unique ticker_names from list of queries"""
    ticker_names = [q.ticker_name for q in query_items]
    return list(set(ticker_names))

def get_ticker_info(ticker_name, **kwargs):
    ticker = yf.Ticker(ticker_name)
    return ticker.info

def create_new_entry(ticker_name, add_form):
    """creates new query from add_form, but first checks if a similar entry already exists and therefore
    can populate some fields using existing information"""
    #check if similar ticker already exists 
    query_item = PortfolioItem.query.filter_by(user=current_user, ticker_name=ticker_name).first()
    args_dict = {'user': current_user,
    'ticker_name': ticker_name, 
    'purchase_price': add_form.purchase_price.data,
    'quantity': add_form.quantity.data}

    if query_item is None:
        ticker_info = get_ticker_info(ticker_name)
        args_dict.update({'currency': ticker_info['currency'], 
                        'sector': ticker_info['sector']})
    else:
        args_dict.update({'currency': query_item.currency, 
                        'sector': query_item.sector})
    item = PortfolioItem(**args_dict)
    return item

def init_summary_row_item():
    item = TickerItem_Portfolio('empty')
    item.ticker_link = 'TOTAL'
    item.ticker = 'summary'
    return item


def consolidate_query_items(query_items):
    """consolidate query items into a dict
    ticker_name: [avg_purchase_price, total_quantity, currency]"""
    ticker_names = list(set([item.ticker_name for item in query_items]))
    avg_prices = []
    total_quantities = []
    currencies = []
    for name in ticker_names:
        ticker_items = [item for item in query_items if item.ticker_name == name]
        prices = [float(item.purchase_price) for item in ticker_items]
        quantitites = [float(item.quantity) for item in ticker_items]
        avg_price = np.average(prices, weights=quantitites)
        avg_prices.append(avg_price)
        total_quantities.append(sum(quantitites))
        currencies.append(ticker_items[0].currency)
    return {n:[p,q,c] for n,p,q,c in zip(ticker_names, avg_prices, total_quantities, currencies)}

def get_dict_exch_rates(items_dict):
    user_currency = current_user.currency
    currencies = [props[2] for (name, props) in items_dict.items()]
    currencies = list(set([c for c in currencies]))
    exch_rates = [query_exchange_rate(c, user_currency) if c != user_currency else 1 for c in currencies]
    exch_rates = dict(zip(currencies, exch_rates))
    return exch_rates

def get_summary_row(query_items, table_items, empty=False):
    """makes more sense to use table_items as well b/c already obtained current prices and everything"""

    def current_price_from_table_items(ticker_name, table_items):
        item = [item for item in table_items if item.ticker == ticker_name]
        assert len(item) == 1
        item = item[0]
        return item.current_price

    #initialize an empty item 
    if query_items is None:
        empty = True
    elif len(query_items) == 0:
        empty = True

    item = init_summary_row_item()
    user_currency = current_user.currency
    user_currency_symbol = CurrencySymbols.get_symbol(user_currency)

    if not empty:
        query_items = consolidate_query_items(query_items)
        original_value = 0
        market_value = 0
        gain = 0

        #get exchange rate ahead of time so not making duplicated requests
        exch_rates = get_dict_exch_rates(query_items)

        for ticker_name in query_items:
            ticker_props = query_items[ticker_name]
            current_price = current_price_from_table_items(ticker_name, table_items)
            exch_rate = exch_rates[ticker_props[2]]

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
    else:
        item.market_value = user_currency_symbol + '0'
        item.gain = user_currency_symbol + '0'
        item.percent_gain = '0'
    return item

def get_query_items_purchase_value(query_items):
    items_dict = consolidate_query_items(query_items)
    exch_rates = get_dict_exch_rates(items_dict)
    purchase_value = 0
    for (ticker_name, props) in items_dict.items():
        purchase_value += (props[0] * props[1] * exch_rates[props[2]])
    return purchase_value

def update_summary_row(query_items=None, ticker_item=None, sum_market_value=None,
                        ticker_market_value=None, ticker_current_value=None, ticker_currency=None, mode="add"):
    """updates summary rows for adding or deleting ticker
    add arguments - query_items, ticker_item, sum_market_value
    delete arguments - query_items, ticker_market_value, ticker_currency, sum_market_value"""
    item = init_summary_row_item()
    user_currency = current_user.currency
    user_currency_symbol = CurrencySymbols.get_symbol(user_currency)
    curr_market_value = float(sum_market_value.strip(user_currency_symbol))
    #get purchase value, subtract from market_value to get gain, and get current value of ticker
    query_purchase_value = get_query_items_purchase_value(query_items)

    if mode == "add":
        exch_rate = query_exchange_rate(ticker_item.currency, user_currency) if ticker_item.currency != current_user.currency else 1
        ticker_current_price = stockquotes.Stock(ticker_item.ticker_name).current_price
        ticker_purchase_price = ticker_item.purchase_price
        ticker_quantity = ticker_item.quantity

        curr_ticker_value = float(ticker_current_price) * float(ticker_quantity) * exch_rate
        new_market_value = round(float(curr_market_value) + float(curr_ticker_value), 2)
    elif mode == "delete":
        exch_rate = query_exchange_rate(ticker_currency, user_currency) if ticker_currency != user_currency else 1
        curr_ticker_value = float(ticker_market_value[1:]) * exch_rate
        new_market_value = round(curr_market_value - curr_ticker_value, 2)
    else:
        raise Exception('invalid mode for updating summary row')

    gain = round(new_market_value - query_purchase_value, 2)
    percent_gain = round((gain/query_purchase_value)*100, 2)

    item.market_value = user_currency_symbol + str(new_market_value)
    item.gain = user_currency_symbol + str(gain)
    item.percent_gain = str(percent_gain)
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

    def delete_btn(self, url):
        #overriding to provide additional succesfunc for updating summary row 
        return f"""
        <button type='button' 
        class='btn btn-outline-danger del-btn btn-sm' 
        style={self.button_styles()}
        id={self.ticker}-delete_btn 
        data-targ-url={url}
        onClick="deleteRow(this, successFunc=deleteSuccess, errorFunc=null, waitFunc=null, dataFunc=deleteRowDataFunc)">
        <i class="fas fa-minus-circle" style="font-size: 12.5px;"></i> 
        </button>
        """

class PortfolioTable(Table_):
    def __init__(self, *args, **kwargs):
        super(PortfolioTable, self).__init__(*args, **kwargs)
    
    classes = ['table', 'table-hover', 'table-sm', 'table-collapse']
    arrow_icon = Col_('ICON', hide_header=True)
    ticker_link = Col_('TICKER')
    purchase_price = Col_('PURCHASE PRICE')
    quantity = Col_('QUANTITY')
    current_price = Col_('CURRENT PRICE')
    market_value = Col_('MARKET VALUE')
    gain = Col_('GAIN', use_item_attrs=True)
    percent_gain = Col_('PERCENT GAIN', use_item_attrs=True)
    delete = Col_('DELETE', hide_header=True)
    table_id = 'portfolio-table'


