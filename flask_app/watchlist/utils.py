from flask_table import Col
from flask_table.html import _format_attrs, element
from flask import url_for
from flask_login import current_user
import itertools
from ..models import WatchlistItem, WatchlistItemTag
from ..utils.table_helpers import (Col_, TickerItem, Table_,
                                    get_table_ncols)
import yfinance as yf
import pandas as pd
from ..config import Config
from .. import db

def watchlist_add_item(ticker_name):
    ticker_info = yf.Ticker(ticker_name).info
    item = WatchlistItem(ticker_name=ticker_name, user=current_user,
    sector=get_sector(ticker_info=ticker_info), exchange=ticker_info['exchange'],
    timezone=ticker_info['exchangeTimezoneName'])
    db.session.add(item)
    db.session.commit()

def get_sector(ticker_name=None, ticker_info=None):
    try:
        if ticker_info is None:
            assert ticker_name is not None
            ticker_info = yf.Ticker(ticker_name).info
        sector = ticker_info['sector']
        return sector
    except KeyError:
        #try to see if it's a crypto
        if ticker_info['quoteType'] == 'CRYPTOCURRENCY':
            return 'CreepToe'
        else:
            return 'N/A'
    except Exception as e:
        print(f'Error in obtaining ticker sector: {e}')
        return 'N/A'


def create_new_tag_entry(new_tag, ticker_name):
    """check if tag for ticker exists, if it doesn't create new entry, else return exception"""
    ticker_item = WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker_name).first()
    current_tags = WatchlistItemTag.query.filter_by(item=ticker_item, tag_content=new_tag).first()
    if current_tags:
        #if new_tag already exists:
        raise Exception('Tag already exists for this ticker!')
    else:
        #create a new entry 
        item = WatchlistItemTag(item=ticker_item, tag_content=new_tag)
        return item

def span_from_tag_item(item, include_delete=True):
    item_id = item.id
    content = item.tag_content
    ticker_name = WatchlistItem.query.get(item.ticker_id).ticker_name
    url = url_for('watchlist.delete_tag')
    if include_delete:
        delete = f"""<a href='#' onClick='deleteTagAjax(this, "{url}")' id="delete-{item_id}" class='tag-delete'><i class='fas fa-times'></i></i></a>"""
    else:
        delete = ''
    return f'<span class="badge bg-info" id="tag-{item_id}">{content} {delete}</span>'

def get_sector_btn(user, ticker_name):
    sector = WatchlistItem.query.filter_by(user=user, ticker_name=ticker_name).first().sector
    url = url_for('watchlist.edit_sector')
    return f"""<button class="btn btn-outline-info btn-sm" onClick="sectorBtnToTextArea(this, '{url}')" id={ticker_name}-sector-btn>{sector}</button>"""


class TickerItem_Watchlist(TickerItem):
    """object to pass to flask table"""
    def __init__(self, *args, **kwargs):
        super(TickerItem_Watchlist, self).__init__(*args, **kwargs)
        self.day_gain = self.empty_or_attr(attr=[], func=self.get_day_gain)
        self.percent_gain = self.empty_or_attr(attr=[], func=self.get_percent_gain)
        self.tag_icon = self.empty_or_attr(attr=[], func=self.tag_icon)
        self.add_notes = self.empty_or_attr(attr=[], func=self.add_notes_btn)
        self.tags =  self.empty_or_attr(attr=[current_user, self.ticker], func=self.get_ticker_tags)
        self.tags_textarea = self.empty_or_attr(attr=[self.ticker], func=self.get_tag_text_area)
        self.sector = self.empty_or_attr(attr=[current_user, self.ticker], func=get_sector_btn)
        self.notes = self.empty_or_attr(attr=[current_user, self.ticker], func=self.get_ticker_notes)
        self.delete = self.empty_or_attr(attr=[url_for('watchlist.delete')], func=self.delete_btn)
        try:
            self.update_html_attrs(self.color_style())
        except:
            pass

    def get_day_gain(self):
        return float(self.ticker_obj.increase_dollars)

    
    def get_percent_gain(self):
        return float(self.ticker_obj.increase_percent)

            
    @staticmethod
    def tag_icon():
        """just returns a tag icon for now, but can customise later"""
        return '<i class="fas fa-tag" style="vertical-align: middle;"></i>'
    
    def add_notes_btn(self):
        return f"""
        <button type='button'
        class='btn btn-outline-info btn-sm' 
        style={self.button_styles()}
        id={self.ticker}-notes_btn
        data-targ-url="{url_for('watchlist.get_notes')}"
        onClick="toggleNotes(this)">
        <i class="bi bi-sticky"></i>
        </button>
        """

    def color_style(self):
        """simple color style to make positive gains green and negative gains red"""
        if self.day_gain != 0:
            if self.day_gain > 0:
                color = self.green_hex
            elif self.day_gain < 0:
                color = self.red_hex
        return {'style': f"color: {color} !important;"}

    @staticmethod
    def get_ticker_notes(user, ticker_name):
        return WatchlistItem.query.filter_by(user=user, ticker_name=ticker_name).first().notes

    def get_ticker_tags(self, user, ticker_name):
        #I'd prefer returning a plus sign that can toggle textarea instead of it just sitting there
        ticker_id = WatchlistItem.query.filter_by(user=user, ticker_name=ticker_name).first().id
        tags = WatchlistItemTag.query.filter_by(ticker_id=ticker_id).all()
        if len(tags) == 0:
            return ''
        else:
            tag_spans = [span_from_tag_item(item) for item in tags]
            span_html = ''.join(tag_spans)
            return span_html

    @staticmethod
    def get_tag_text_area(ticker_name):
        return f"""<textarea class="form-control"
        style="font-size: 11px; height: 2.5em; width: 8em;"
        id={ticker_name}-tags-text-area
        placeholder="Add a tag!"></textarea>"""

class WatchlistTable(Table_):
    def __init__(self, *args, use_item_notes=False, **kwargs):
        super(WatchlistTable, self).__init__(*args, **kwargs)
        self.use_item_notes = use_item_notes
        self.table_id = 'watchlist-table'

    #these define class definitions, and are gone once class/instance has been initialized?
    classes = ['table', 'table-hover', 'table-sm', 'table-collapse']
    tag_icon = Col_('ICON', hide_header=True, td_html_attrs={"style": "color: #274156; font-size: 12.5px;" })
    ticker_link = Col_('TICKER')
    current_price = Col('CURRENT PRICE')
    day_gain = Col_('DAY GAIN', use_item_attrs=True)
    percent_gain = Col_('PERCENT GAIN', use_item_attrs=True)
    tags = Col_('TAGS')
    tags_textarea = Col_('ADD TAGS', hide_header=True)
    sector = Col_('SECTOR')
    add_notes = Col_('ADD_NOTES', hide_header=True)
    delete = Col_('DELETE', hide_header=True)

    def tbody(self):
        out = [self.tr(item) for item in self.items]
        if self.use_item_notes:
            notes = [self.get_notes_tr(item) for item in self.items]
            out = list(itertools.chain(*zip(out, notes)))
        if not out:
            return ''
        content = '\n{}\n'.format('\n'.join(out))
        return element('tbody', content=content, escape_content=False)


#section to deal with notes text area in table 
def save_notes_btn(ticker):
    return f"""<button type="button"
    class='btn btn-outline-info btn-sm' 
    style={TickerItem_Watchlist('empty').button_styles()}
    id={ticker}-notes-save
    data-targ-url={url_for('watchlist.save_notes')}
    onClick="saveNotes(this)">
    <i class="bi bi-save"></i>
    </button>
    """

def notes_textarea(ticker, ticker_notes):
    return f"""<textarea class="form-control"
    style="font-size: 13px;"
    rows="5"
    id={ticker}-text-area
    placeholder="Enter your notes here!">{ticker_notes}</textarea>
    """

def get_notes_tr(ticker):
    n_cols = get_table_ncols(class_=WatchlistTable)
    #dummy string to allow colspan in jquery datatables
    dummy_string = [f'<td id="{ticker}+-notes-{i}"></td>' for i in range(3,n_cols)]
    dummy_string = ''.join(dummy_string)

    td_attrs = {"colspan": str(n_cols), 'align': 'right'}
    tr_attrs = {"id": ticker+'-notes'}
    formatted_td_attrs = _format_attrs(td_attrs)
    formatted_tr_attrs = _format_attrs(tr_attrs)

    #get ticker notes from database 
    query = WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker).first()
    ticker_notes = query.notes
    return f"""<tr {formatted_tr_attrs}>
    <td {formatted_td_attrs}>
    {notes_textarea(ticker, ticker_notes)}
    {save_notes_btn(ticker)}
    </td>
    {dummy_string}
    </tr>"""

    
