from flask_table import Col, Table
from flask_table.html import element
from flask import Markup, jsonify, url_for
import stockquotes
from ..models import WatchlistItem
import time 

def get_table_ncols(class_=None):
    item_attrs = class_.__dict__.values()
    n_cols = len([a for a in item_attrs if isinstance(a, Col)])
    return n_cols

def update_attr_dict(attr_dict, new_attr):
    keys = list(attr_dict.keys())
    new_key = list(new_attr.keys())[0]
    if new_key in keys:
        attr_dict[new_key] = ' '.join([attr_dict[new_key], new_attr[new_key]])
    else:
        attr_dict.update(new_attr) 


class TickerItem:
    """base class to create object to pass to flask table"""
    def __init__(self, ticker):
        self.empty = ticker == 'empty'
        self.ticker = self.empty_or_attr(ticker.upper())
        self.ticker_link = self.get_ticker_link()
        self.ticker_obj = self.empty_or_attr(attr=ticker, func=stockquotes.Stock)
        self.current_price = self.empty_or_attr(attr=[self.ticker_obj, 'current_price'], func=getattr)
        self.html_attrs = {}
        self.green_hex = "#027E4A"
        self.red_hex = "#EF3125"
        try:
            self.update_html_attrs(self.color_style())
        except:
            pass
            
    @staticmethod
    def tag_icon():
        """just returns a tag icon for now, but can customise later"""
        return '<i class="fas fa-tag" style="vertical-align: middle;"></i>'

    def delete_btn(self, url):
        return f"""
        <button type='button' 
        class='btn btn-outline-danger del-btn btn-sm' 
        style={self.button_styles()}
        id={self.ticker}-delete_btn 
        data-targ-url={url}
        onClick="deleteRow(this)">
        <i class="fas fa-minus-circle" style="font-size: 12.5px;"></i> 
        </button>
        """
    
    def update_html_attrs(self, new_attr):
        update_attr_dict(self.html_attrs, new_attr)

    
    def get_ticker_link(self):
        link = f"""<a href="{url_for('searches.search_redirect', q=self.ticker)}"
        style="color: black;">{self.ticker}</a>"""
        return link

    def empty_or_attr(self, attr, func=None):
        if self.empty:
            return ''
        else:
            if func is not None:
                out = func(attr) if type(attr) is not list else func(*attr)
            else:
                out = attr
            return out


    @staticmethod
    def button_styles():
        return """
        'border: 0px; background-color:transparent; padding: 1px 2px;'
        """


class Col_(Col):
    def __init__(self, *args, use_item_attrs=False, hide_header=False, **kwargs):
        super(Col_, self).__init__(*args, **kwargs)
        self.use_item_attrs = use_item_attrs
        self.hide_header = hide_header
        if self.hide_header:
            self._hide_header()

    def td_format(self, content, escaped=False):
        """just to provide a bit more flexibility to escape or not escape"""
        if escaped:
            return Markup.escape(content)
        else:
            return content

    def add_html_id_attr(self, item, html_attrs, attr):
        html_attrs.update({'id': f"{item.ticker}-{attr}"})

    def td(self, item, attr, id_attr=True):
        """add option to import tag attrs from item itself - item tag attrs override td_html_attrs"""
        content = self.td_contents(item, self.get_attr_list(attr))
        if len(item.html_attrs) and self.use_item_attrs:
            td_html_attrs = item.html_attrs
        else:
            td_html_attrs = self.td_html_attrs 

        if id_attr:
            self.add_html_id_attr(item, td_html_attrs, attr)
        
        return element(
            'td',
            content=content,
            escape_content=False,
            attrs=td_html_attrs)

    def _hide_header(self):
        update_attr_dict(self.th_html_attrs, {"style": "color: rgba(0, 0, 0, 0);"})


class Table_(Table):
    def __init__(self, *args, **kwargs):
        super(Table_, self).__init__(*args, **kwargs)

    @staticmethod
    def get_tr_attrs(item):
        return {'id': f"{item.ticker}"}


def new_item_json(item, table_class=None, include_id=False, **kwargs):
    """creates a json for table items to be sent to client side. use kwargs to include any additional 
    items to be sent over"""
    dummy_table = table_class(items=[])
    if item.empty:
        #if item is empty then just send a truthy value 
        item_dict = {'newItem': False}
    else:
        item_dict = {'newItem': dummy_table.tr(item)}

    for key, val in kwargs.items():
        item_dict.update({key: dummy_table.tr(val)})
    if include_id:
        item_dict.update({'id': item.ticker})
    return jsonify(item_dict)

def query_to_table_items(query_items, item_class):
    """converts db items (which just involves ticker_name, date_posted) to TickerItem object"""
    return [item_class(ticker_name) for ticker_name in [q.ticker_name for q in query_items]]

def ticker_name_to_table_items(ticker_names, item_class):
    return [item_class(ticker_name) for ticker_name in ticker_names]

