from flask_table import Col
from flask_app.utils.table_helpers import (Col_, TickerItem, 
                                Table_)
from flask_login import current_user 
from flask_app.watchlist.utils import get_sector
from flask_app.models import PortfolioOrder, ExchangeRate, Position, User
import numpy as np 
import yfinance as yf
from flask_app import db
from currency_symbols import CurrencySymbols
import requests
from datetime import datetime
from flask_app.utils.helpers import html_formatter, subscribe_user, unsubscribe_user
from yfQuotes import get_quotes_asyncio
from flask_app.utils.helpers import get_quote_object

def query_exchange_rate(from_currency, to_currency):
    """basically check the database to see if there is this entry, if not then get it from api
    - rates are updated once a day"""
    query = ExchangeRate.query.filter_by(from_currency=from_currency, to_currency=to_currency).first()
    if query:
        #check if it has been updated today 
        if query.date_updated == str(datetime.today().date()):
            #print('rate up to date')
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
            #print('rate updated at: ', query.date_updated)
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

def get_exchange_rate(from_currency, to_currency, apikey='761WW05Z48CV56CK', testing=False, datetime_format='%Y-%m-%d'):
    if not testing:
        """Get fx rate from alphavantage free api:)"""
        url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&apikey={apikey}'
        r = requests.get(url)
        r_body = r.json()['Time Series FX (Daily)']
        dates = [datetime.strptime(date, datetime_format) for date in r_body]
        latest_date = max(dates).strftime(datetime_format)
        latest = r_body[latest_date]
        rate = float(list(latest.values())[-1])
        #here adjust for fact that GBp indicates trading in pence
        if from_currency == 'GBp':
            rate /= 100
        elif to_currency == 'GBp':
            rate *= 100
    else:
        return 1
    return rate

def get_unique_ticker_names(query_items):
    """just returns unique ticker_names from list of queries"""
    ticker_names = [q.ticker_name for q in query_items]
    return list(set(ticker_names))

def get_ticker_info(ticker_name):
    ticker = yf.Ticker(ticker_name)
    return ticker.info

def get_current_purchase_price(ticker_name, current_user):
    #get current purchase price based on current position
    position = Position.query.filter_by(user=current_user, ticker_name=ticker_name).first()
    if position:
        return position.avg_purchase_price
    else:
        print('You do not own any shares!')
        return 0
    
def create_new_order_entry(ticker_name, form, form_type='buy'):
    """creates new query from add_form, but first checks if a similar entry already exists and therefore
    can populate some fields using existing information"""
    #HERE for sell order entries need to add current avg purchase price 
    #check if similar ticker already exists 
    query_item = PortfolioOrder.query.filter_by(user=current_user, ticker_name=ticker_name).first()
    args_dict = {'user': current_user,
    'ticker_name': ticker_name, 
    'quantity': form.order_quantity.data,
    }

    if form_type == 'sell':
        args_dict.update({'order_type': '0'})
        args_dict.update({'sell_price': form.order_price.data})
        args_dict.update({'purchase_price': get_current_purchase_price(ticker_name, current_user)})
    elif form_type == 'buy':
        args_dict.update({'purchase_price': form.order_price.data})
    else:
        raise Exception('invalid form type')

    if query_item is None:
        ticker_info = get_ticker_info(ticker_name)
        sector = get_sector(ticker_info=ticker_info)
        args_dict.update({'currency': ticker_info['currency'], 
                        'sector': sector})
    else:
        args_dict.update({'currency': query_item.currency, 
                        'sector': query_item.sector})
    item = PortfolioOrder(**args_dict)

    db.session.add(item)
    db.session.commit()
    return item

def update_position(ticker_name, item, mode='buy'):
    #create a new position entry if this doesn't previously exist, or update an existing one 
    """modes: 1 - buy order
    0 - sell order"""
    assert mode in ['buy', 'sell']
    position = Position.query.filter_by(ticker_name=ticker_name, user=current_user).first()

    if position:
        current_purchase_price = float(position.avg_purchase_price)
        current_quantity = float(position.quantity)
        item_purchase_price = float(item.purchase_price)
        item_quantity = float(item.quantity)
        #update according to order 
        if mode == 'buy':
            #get new share price and update quantity
            position.avg_purchase_price = np.average([current_purchase_price, item_purchase_price],
            weights=[current_quantity, item_quantity])
            position.quantity = current_quantity + item_quantity
            db.session.commit()

        elif mode == 'sell':
            #update quantity
            if current_quantity - item_quantity == 0:
                db.session.delete(position)
                db.session.commit()

                #check if should still subscribe - if not then remove relationship
                quote = get_quote_object(ticker_name, None)
                unsubscribe_user(User.query.get(current_user.get_id()), quote)
            else:
                position.quantity = current_quantity - item_quantity
                db.session.commit()
            #if quantity = 0 then delete the entry
    elif not position and mode == 'buy':
        position = Position(ticker_name=item.ticker_name,
        avg_purchase_price=item.purchase_price, quantity=item.quantity,
        currency=item.currency, user=current_user)
        db.session.add(position)
        db.session.commit()
        #b/c it's a new buy order and not subscribed to quote, subscribe here 
        ticker_info = yf.Ticker(ticker_name).info
        quote = get_quote_object(ticker_name, ticker_info)
        subscribe_user(User.query.get(current_user.get_id()), quote)

    elif not position and mode == 'sell':
        raise Exception('Cannot create sell order without owning any shares!')
    return position

def init_summary_row_item():
    item = TickerItem_Portfolio('empty')
    item.ticker_link = 'TOTAL'
    item.ticker = 'summary'
    return item

#change this function so that sell function operates fine ###############
# - change this to account for the fact that there could be sell orders
def consolidate_query_items(query_items, order_type='1'):
    """consolidate query items into a dict
    ticker_name: [avg_purchase_price, total_quantity, currency]
    item_type: 1 = BUY ORDERS,  0 = SELL ORDERS, 2 = OWNED"""
    assert order_type in ['0', '1']
    ticker_names = list(set([item.ticker_name for item in query_items]))
    avg_prices = []
    total_quantities = []
    currencies = []
    for name in ticker_names:
        #separate owned/sold orders here 
        ticker_items = [item for item in query_items if item.ticker_name == name]
        ticker_items = [item for item in query_items if item.order_type == order_type]
        if order_type == '1':
            prices = [float(item.purchase_price) for item in ticker_items]
        elif order_type == '0':
            prices = [float(item.sell_price) for item in ticker_items]
        quantities = [float(item.quantity) for item in ticker_items]
        avg_price = np.average(prices, weights=quantities)
        avg_prices.append(avg_price)
        quantities = sum(quantities)
        total_quantities.append(quantities)
        currencies.append(ticker_items[0].currency)
    return {n:[p,q,c] for n,p,q,c in zip(ticker_names, avg_prices, total_quantities, currencies)}

def get_positions_exch_rates(position):
    user_currency = current_user.currency
    currencies = [o.currency for o in position]
    currencies = list(set([c for c in currencies]))
    exch_rates = [query_exchange_rate(c, user_currency) if c != user_currency else 1 for c in currencies]
    exch_rates = dict(zip(currencies, exch_rates))
    return exch_rates

def get_summary_row(table_items, empty=False):
    """makes more sense to use table_items as well b/c already obtained current prices and everything"""

    def current_price_from_table_items(ticker_name, table_items):
        item = [item for item in table_items if item.ticker == ticker_name]
        assert len(item) == 1
        item = item[0]
        return item.current_price

    #initialize an empty item 
    if table_items is None:
        empty = True
    elif len(table_items) == 0:
        empty = True

    item = init_summary_row_item()
    user_currency = current_user.currency
    user_currency_symbol = CurrencySymbols.get_symbol(user_currency)

    #mainly need to modify this function... no need to use consolidate query itesm 
    if not empty:
        positions = [item.position for item in table_items]
        original_value = 0
        market_value = 0
        gain = 0
        #get exchange rate ahead of time so not making duplicated requests
        exch_rates = get_positions_exch_rates(positions)

        for ticker in positions:
            current_price = current_price_from_table_items(ticker.ticker_name, table_items)
            exch_rate = exch_rates[ticker.currency]
            quantity = float(ticker.quantity)
            avg_purchase_price = float(ticker.avg_purchase_price)

            current_value = current_price * quantity * exch_rate
            purchase_value = avg_purchase_price * quantity * exch_rate

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

#change this to use  instead of query_items?
def get_position_purchase_value(position):
    purchase_value = 0
    if len(position) > 0:
        exch_rates = get_positions_exch_rates(position)
        for ticker in position:
            purchase_value += (float(ticker.avg_purchase_price) * float(ticker.quantity) * exch_rates[ticker.currency])

    return purchase_value


#edit tickeritem portfolio so that it consolidates all the purchase orders
class TickerItem_Portfolio(TickerItem):
    """object to pass to portfolio table -- 
    returns the total position across all purchases/sales of the ticker"""
    def __init__(self, *args, **kwargs):
        super(TickerItem_Portfolio, self).__init__(*args, **kwargs)
        self.n_places = 2
        self.position = self.empty_or_attr(attr=[{'user': current_user, 'ticker_name': self.ticker}], func=self.get_position)
        if self.position is None:
            self.empty = True
        print(self.position)
        #filter out items that have status SOLD
        self.purchase_price = self.empty_or_attr(attr=[], func=self.get_purchase_price)
        self.gain = self.empty_or_attr(attr=[], func=self.get_gain)
        self.percent_gain = self.empty_or_attr(attr=[], func=self.get_percent_gain)
        self.quantity = self.empty_or_attr(attr=[], func=self.get_quantity)
        self.market_value = self.empty_or_attr(attr=[], func=self.get_market_value)
        self.arrow_icon = self.empty_or_attr(attr=[], func=self.get_arrow_icon)
        self.exch_rate = self.empty_or_attr(attr=[], func=self.get_exch_rate)
        #have a sell button? I dunno
        try:
            self.update_html_attrs(self.color_style())
        except Exception as e:
            print(e)
        
        print('TickerItemPortfolio initialised')
            
    def get_exch_rate(self):
        rate = get_positions_exch_rates([self.position])
        return list(rate.values())[0]

    def get_purchase_price(self):
        price = float(self.position.avg_purchase_price)
        return round(price, self.n_places)

    def get_quantity(self):
        """need to account for shares sold"""
        n_shares = float(self.position.quantity)
        print(n_shares)
        return round(n_shares, self.n_places)

    def get_gain(self):
        return round(self.current_price - self.purchase_price, self.n_places)
    
    def get_percent_gain(self):
        return round((self.gain/self.purchase_price)*100, self.n_places)

    @staticmethod
    def get_position(arg_dict):
        return Position.query.filter_by(**arg_dict).first()

    def get_market_value(self):
        currency = self.position.currency
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

    def get_arrow_icon(self):
        """give an green up arrow or red down arrow depending on status"""
        if self.gain > 0:
            return html_formatter('i', cls=["fas fa-arrow-alt-circle-up"],style="color:#027E4A;")
        elif self.gain < 0:
            return html_formatter('i', cls=["fas fa-arrow-alt-circle-down"],style="color:#EF3125;")
        elif self.gain == 0:
            return html_formatter('i', cls=["fas fa-dot-circle"])

    
    def __repr__(self):
        return f"TickerItem_Portfolio({self.ticker_name})"
    
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
    exch_rate = Col_('EXCH RATE')

    table_id = 'portfolio-table'

    def __repr__(self):
        return "PortfolioTable"

