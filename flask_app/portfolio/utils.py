from flask_table import Table, Col
from ..utils.table_helpers import Col_, TickerItem
from flask_login import current_user 
import stockquotes
from ..models import PortfolioItem, Portfolio
import numpy as np 
import yfinance as yf

def get_portfolio_items(arg_dict):
    """pass query params to get porfolio items
    - if you want to query items using user, pass {'user': current_user}"""
    if 'user' in arg_dict.keys():
        arg_dict.update({'portfolio': get_user_portfolio(arg_dict['user'])})
        del arg_dict['user']
    return PortfolioItem.query.filter_by(**arg_dict).order_by(PortfolioItem.ticker_name.desc()).all()

def get_user_portfolio(user):
    return Portfolio.query.filter_by(user=user).first()

def get_ticker_currency(ticker_name):
    ticker = yf.Ticker(ticker_name)
    return ticker.info['currency'].strip().upper()

class TickerItem_Portfolio(TickerItem):
    """object to pass to portfolio table -- 
    returns the total position across all purchases of the ticker"""
    def __init__(self, *args, **kwargs):
        super(TickerItem_Portfolio, self).__init__(*args, **kwargs)
        self.purchase_price = self.empty_or_attr(attr=[current_user, self.ticker], func=self.get_avg_purchase_price)
        self.gain = self.empty_or_attr(attr=[self.current_price, self.purchase_price], func=self.get_gain)
        self.percent_gain = self.empty_or_attr(attr=[self.gain, self.purchase_price], func=self.get_percent_gain)
        self.quantity = self.empty_or_attr(attr=[current_user, self.ticker], func=self.get_total_quantity)
        self.arrow_icon = self.empty_or_attr(attr=[], func=self.arrow_icon)
        #self.delete = self.empty_or_attr(self.delete_btn())
        #have a sell button? I dunno

    def arrow_icon(self):
        """give an green up arrow or red down arrow depending on status"""
        if self.gain > 0:
            return '<i class="fas fa-arrow-alt-circle-up" style="color:#027E4A;"></i>'
        elif self.gain < 0:
            return '<i class="fas fa-arrow-alt-circle-down" style="color:#EF3125;"></i>'
        elif self.gain == 0:
            return '<i class="fas fa-dot-circle"></i>'

    @staticmethod
    def get_avg_purchase_price(user, ticker_name):
        purchases = get_portfolio_items({'user': current_user, 'ticker_name': ticker_name})
        quantities = [float(p.quantity) for p in purchases]
        prices = [float(p.purchase_price) for p in purchases]
        return np.average(prices, weights=quantities)

    @staticmethod 
    def get_total_quantity(user, ticker_name):
        purchases = get_portfolio_items({'user': current_user, 'ticker_name': ticker_name})
        return sum([float(p.quantity) for p in purchases])

    @staticmethod
    def get_gain(current_price, purchase_price, n_places=2):
        return round(current_price - purchase_price, n_places)
    
    @staticmethod
    def get_percent_gain(gain, purchase_price, n_places=2):
        return round((gain/purchase_price)*100, 2)

class PortfolioTable(Table):
    def __init__(self, *args, **kwargs):
        super(PortfolioTable, self).__init__(*args, **kwargs)
    
    classes = ['table', 'table-hover', 'table-sm', 'table-collapse']
    arrow_icon = Col_('ICON', hide_header=True)
    ticker_link = Col_('TICKER')
    purchase_price = Col('PURCHASE PRICE')
    quantity = Col('QUANTITY')
    current_price = Col('CURRENT PRICE')
    gain = Col('GAIN')
    percent_gain = Col('PERCENT GAIN')
    table_id = 'portfolio-table'