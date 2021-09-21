from flask import Blueprint, request, jsonify, url_for
from ..utils.helpers import _render_template, format_ticker_name, form_errors_400, redirect_next_page
from ..utils.table_helpers import ticker_name_to_table_items, new_item_json
from ..models import PortfolioOwnership, PortfolioItem
from .forms import AddForm, SellForm
from .utils import (PortfolioTable, TickerItem_Portfolio, get_unique_ticker_names,
                    get_summary_row, create_new_order_entry, update_summary_row,
                    update_ownership)
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
def get_table():
    try:
        ownership = PortfolioOwnership.query.filter_by(user=current_user).all()
        if len(ownership) == 0:
            table = PortfolioTable(items=[get_summary_row(None, None, empty=True)])
            empty = 1
        else:
            #update porfolio stats
            table_items = ticker_name_to_table_items(get_unique_ticker_names(ownership), TickerItem_Portfolio)
            #create an empty item, then update attrs to make summary row
            table_items.append(get_summary_row(ownership, table_items))
            table = PortfolioTable(items=table_items)
            empty = 0
        
        return jsonify({'table': table, 'empty': empty})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})
    


@portfolio.route('/portfolio/add', methods=["GET", "POST"])
@login_required
def add():
    add_form = AddForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            ticker_name = format_ticker_name(add_form.ticker_name.data)
            #just add entry here
            item = create_new_order_entry(ticker_name, add_form)
            ### update ownership entry here 
            update_ownership(ticker_name, item, mode='1')
            current_ownership = PortfolioOwnership.query.filter_by(user=current_user).all()
            #update summary row - instead of creating new one, just subtract current values from deleted row and current sum row 
            return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                                summary=update_summary_row(ownership=current_ownership, ticker_item=item,
                                                        request_json=request.json, mode="add"))        
        else:
            print(add_form.errors)
            return form_errors_400(add_form)
    else:
        redirect_next_page()

@portfolio.route('/portfolio/sell', methods=["POST"])
@login_required
def sell():
    sell_form = SellForm()
    try:
        print(sell_form.ticker_name.data)
        if sell_form.validate_on_submit():
            ticker_name = format_ticker_name(sell_form.ticker_name.data)
            item = create_new_order_entry(ticker_name, sell_form, form_type='sell')
            #update ownership entry here 
            update_ownership(ticker_name, item, mode='0')
            current_ownership = PortfolioOwnership.query.filter_by(user=current_user).all()
            #problem in tickeritem_portfolio -- if no remaining shares of ticker left - 
            return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                                summary=update_summary_row(ownership=current_ownership, ticker_item=item,
                                                        request_json=request.json, mode='sell'))
        else:
            print(sell_form.errors)
            return form_errors_400(sell_form)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})
