from flask import Blueprint, request, jsonify, url_for
from ..utils.helpers import _render_template, format_ticker_name, redirect_next_page
from ..errors.utils import error_500_handler, form_errors_400
from ..utils.table_helpers import query_to_table_items, new_item_json
from ..models import Position, PortfolioItem
from .forms import AddForm, SellForm
from .utils import (PortfolioTable, TickerItem_Portfolio, get_unique_ticker_names,
                    get_summary_row, create_new_order_entry, update_summary_row,
                    update_position)
from datetime import datetime
from flask_login import current_user, login_required
from flask_app import db

portfolio = Blueprint('portfolio', __name__)

@portfolio.route('/portfolio', methods=["GET", "POST"])
@login_required
def main():
    add_form = AddForm()
    sell_form = SellForm()
    return _render_template('portfolio/main.html', add_form=add_form, sell_form=sell_form)

@portfolio.route('/portfolio/get_table', methods=["POST"])
@login_required
@error_500_handler
def get_table():
    positions = Position.query.filter_by(user=current_user).all()
    if len(positions) == 0:
        table = PortfolioTable(items=[get_summary_row(None, None, empty=True)])
        empty = 1
    else:
        #update porfolio stats
        table_items = query_to_table_items(positions, TickerItem_Portfolio)
        #create an empty item, then update attrs to make summary row
        table_items.append(get_summary_row(positions, table_items))
        table = PortfolioTable(items=table_items)
        empty = 0
    
    return jsonify({'table': table, 'empty': empty})



@portfolio.route('/portfolio/add', methods=["GET", "POST"])
@login_required
@error_500_handler
def add():
    add_form = AddForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            ticker_name = format_ticker_name(add_form.ticker_name.data)
            #just add entry here
            item = create_new_order_entry(ticker_name, add_form)
            ### update position entry here 
            update_position(ticker_name, item, mode='1')
            current_position = Position.query.filter_by(user=current_user).all()
            #update summary row - instead of creating new one, just subtract current values from deleted row and current sum row 
            return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                                summary=update_summary_row(position=current_position, ticker_item=item,
                                                        request_json=request.json, mode="add"))        
        else:
            print(add_form.errors)
            return form_errors_400(add_form)
    else:
        redirect_next_page()


@portfolio.route('/portfolio/sell', methods=["POST"])
@login_required
@error_500_handler
def sell():
    sell_form = SellForm()
    print(sell_form.ticker_name.data)
    if sell_form.validate_on_submit():
        ticker_name = format_ticker_name(sell_form.ticker_name.data)
        item = create_new_order_entry(ticker_name, sell_form, form_type='sell')
        #update position entry here 
        update_position(ticker_name, item, mode='0')
        current_position = Position.query.filter_by(user=current_user).all()
        #problem in tickeritem_portfolio -- if no remaining shares of ticker left - 
        return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                            summary=update_summary_row(position=current_position, ticker_item=item,
                                                    request_json=request.json, mode='sell'))
    else:
        print(sell_form.errors)
        return form_errors_400(sell_form)

