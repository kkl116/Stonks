from flask_table import Table, Col
from flask_table.html import _format_attrs, element
from flask import url_for
from flask_login import current_user
import itertools
from ..models import WatchlistItem
from ..utils.table_helpers import Col_, TickerItem

class TickerItem_Watchlist(TickerItem):
    """object to pass to flask table"""
    def __init__(self, *args, **kwargs):
        super(TickerItem_Watchlist, self).__init__(*args, **kwargs)
        self.day_gain = self.empty_or_attr(self.ticker_obj.increase_dollars)
        self.percent_gain = self.empty_or_attr(self.ticker_obj.increase_percent)
        self.tag_icon = self.empty_or_attr(self.tag_icon())
        self.add_notes = self.empty_or_attr(self.add_notes_btn())
        self.notes = self.empty_or_attr(WatchlistItem.query.filter_by(user=current_user, ticker_name=self.ticker).first().notes)
        self.delete = self.empty_or_attr(self.delete_btn(url_for('watchlist.delete')))
        try:
            self.update_html_attrs(self.color_style())
        except:
            pass
            
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
        onClick="toggleNotes(this)">
        <i class="far fa-sticky-note"></i>
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



class WatchlistTable(Table):
    def __init__(self, *args, use_item_notes=True , **kwargs):
        super(WatchlistTable, self).__init__(*args, **kwargs)
        self.use_item_notes = use_item_notes

    classes = ['table', 'table-hover', 'table-sm', 'table-collapse']
    tag_icon = Col_('ICON', hide_header=True, td_html_attrs={"style": "color: #274156; font-size: 12.5px;" })
    ticker_link = Col_('TICKER')
    current_price = Col('CURRENT PRICE')
    day_gain = Col_('DAY GAIN', use_item_attrs=True)
    percent_gain = Col_('PERCENT GAIN', use_item_attrs=True)
    add_notes = Col_('ADD_NOTES', hide_header=True)
    delete = Col_('DELETE', hide_header=True)
    table_id = 'watchlist-table'

    @staticmethod
    def get_tr_attrs(item):
        return {'id': f"{item.ticker}"}

    @staticmethod
    def save_notes_btn(item):
        return f"""<button type="button"
        class='btn btn-outline-info btn-sm' 
        style={item.button_styles()}
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


