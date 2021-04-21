from flask_table import Table, Col

class Watchlist_Table(Table):
    classes = ['table', 'table-hover', 'table-sm', 'table-borderless' 'table-collapse']
    TICKER = Col('TICKER')
    PRICE = Col('PRICE')
