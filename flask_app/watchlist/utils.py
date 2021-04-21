from flask_table import Table, Col
from stockquotes import Stock

class Watchlist_Stock(Stock):
    """Inherits Stock class, but just adding some additional stuff so it automatically
    creates dicts for flask table"""
    def __init__(self, ticker):


class Watchlist_Table(Table):
    classes = ['table', 'table-hover', 'table-sm', 'table-borderless' 'table-collapse']
    TICKER = Col('TICKER')
    PRICE = Col('PRICE')
