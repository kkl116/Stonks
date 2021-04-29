from flask_table import Table, Col
from flask_table.html import _format_attrs, element
from flask import jsonify, Markup, url_for
from flask_login import current_user
import stockquotes
import itertools
from ..models import WatchlistItem

def button_styles():
    return """
    'border: 0px; background-color:transparent; padding: 1px 2px;'
    """

class TickerItem:
    """object to pass to flask table"""
    def __init__(self, ticker):
        self.empty = ticker == 'empty'
        self.ticker = '' if self.empty else ticker.upper()
        self.ticker_obj = '' if self.empty else stockquotes.Stock(ticker)
        self.current_price = '' if self.empty else self.ticker_obj.current_price 
        self.day_gain = '' if self.empty else self.ticker_obj.increase_dollars
        self.percent_gain = '' if self.empty else self.ticker_obj.increase_percent
        self.tag_icon = '' if self.empty else self.tag_icon()
        self.add_notes = '' if self.empty else self.add_notes_btn()
        self.notes = '' if self.empty else WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker).first().notes
        self.delete = '' if self.empty else self.delete_btn() 
        self.html_attrs = {}
        try:
            self.update_html_attrs(self.color_style())
        except:
            pass
            
    @staticmethod
    def tag_icon():
        """just returns a tag icon for now, but can customise later"""
        return '<i class="fas fa-tag" style="vertical-align: middle;"></i>'

    def delete_btn(self):
        return f"""
        <button type='button' 
        class='btn btn-outline-danger del-btn btn-sm' 
        style={button_styles()}
        id={self.ticker}-delete_btn 
        data-targ-url={url_for('watchlist.delete')}
        onClick="deleteRow(this)">
        <i class="fas fa-minus-circle" style="font-size: 12.5px;"></i> 
        </button>
        """
    
    def add_notes_btn(self):
        return f"""
        <button type='button'
        class='btn btn-outline-info btn-sm' 
        style={button_styles()}
        id={self.ticker}-notes_btn
        onClick="toggleNotes(this)">
        <i class="far fa-sticky-note"></i>
        </button>
        """

    def color_style(self):
        """simple color style to make positive gains green and negative gains red"""
        if self.day_gain != 0:
            if self.day_gain > 0:
                color = "#027E4A"
            elif self.day_gain < 0:
                color = "#EF3125"
        return {'style': f"color: {color} !important;"}

    def update_html_attrs(self, new_attr):
        keys = list(self.html_attrs.keys())
        new_key = list(new_attr.keys())[0]
        if new_key in keys:
            self.html_attrs[new_key] = ' '.join([self.html_attrs[new_key], new_attr[new_key]])
        else:
            self.html_attrs.update(new_attr)


class Col_(Col):
    def __init__(self, *args, use_item_attrs=False , **kwargs):
        super(Col_, self).__init__(*args, **kwargs)
        self.use_item_attrs=use_item_attrs

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



class WatchlistTable(Table):
    def __init__(self, *args, use_item_notes=True , **kwargs):
        super(WatchlistTable, self).__init__(*args, **kwargs)
        self.use_item_notes = use_item_notes

    classes = ['table', 'table-hover', 'table-sm', 'table-borderless' 'table-collapse']
    tag_icon = Col_('ICON', th_html_attrs={"style": "color: rgba(0, 0, 0, 0);"},
                td_html_attrs={"style": "color: #274156; font-size: 12.5px;" })
    ticker = Col('TICKER')
    current_price = Col('CURRENT PRICE')
    day_gain = Col_('DAY GAIN', use_item_attrs=True)
    percent_gain = Col_('PERCENT GAIN', use_item_attrs=True)
    add_notes = Col_('ADD_NOTES', th_html_attrs={"style": "color: rgba(0, 0, 0, 0);"})
    delete = Col_('DELETE', th_html_attrs={"style": "color: rgba(0, 0, 0, 0);"})
    table_id = 'watchlist-table'

    @staticmethod
    def get_tr_attrs(item):
        return {'id': f"{item.ticker}"}

    @staticmethod
    def save_notes_btn(item):
        return f"""<button type="button"
        class='btn btn-outline-info btn-sm' 
        style={button_styles()}
        id={item.ticker}-notes-save
        data-targ-url={url_for('watchlist.save_notes')}
        onClick="saveNotes(this)">
        <i class="far fa-save"></i>
        </button>
        """
    
    @staticmethod
    def notes_textarea(item):
        return f"""<textarea class="form-control"
        style="font-size: 13px;"
        rows="5"
        id={item.ticker}-text-area
        placeholder="Enter your notes here!">{item.notes}</textarea>
        """

    def get_notes_tr(self, item):
        item_attrs = WatchlistTable.__dict__.values()
        n_cols = len([a for a in item_attrs if isinstance(a, Col)])

        td_attrs = {"colspan": str(n_cols), 'align': 'right'}
        tr_attrs = {"id": item.ticker+'-notes', "style":"display:none;"}
        formatted_td_attrs = _format_attrs(td_attrs)
        formatted_tr_attrs = _format_attrs(tr_attrs)
        return f"""<tr {formatted_tr_attrs}>
        <td {formatted_td_attrs}>
        {self.notes_textarea(item)}
        {self.save_notes_btn(item)}
        </td>
        </tr>"""

    def tbody(self):
        out = [self.tr(item) for item in self.items]
        if self.use_item_notes:
            notes = [self.get_notes_tr(item) for item in self.items]
            out = list(itertools.chain(*zip(out, notes)))

        if not out:
            return ''
        content = '\n{}\n'.format('\n'.join(out))
        return element('tbody', content=content, escape_content=False)


def new_item_json(item):
    return jsonify({'newItem': WatchlistTable(items=[]).tr(item)})

def query_to_table_items(query_items):
    """converts db items (which just involves ticker_name, date_posted) to TickerItem object"""
    return [TickerItem(ticker_name) for ticker_name in [q.ticker_name for q in query_items]]

def format_ticker_name(ticker_name):
    return ticker_name.strip().upper()

