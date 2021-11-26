from flask import Blueprint, request, jsonify, url_for
from ..utils.helpers import _render_template, format_ticker_name, redirect_next_page
from ..errors.utils import error_500_handler, form_errors_400
from ..utils.table_helpers import query_to_table_items, new_item_json
from ..models import Position
from .forms import OrderForm
from .utils import (PortfolioTable, TickerItem_Portfolio, get_unique_ticker_names,
                    get_summary_row, create_new_order_entry, update_summary_row,
                    update_position)
from datetime import datetime
from flask_login import current_user, login_required
from flask_app import db
import json

portfolio = Blueprint('portfolio', __name__)

@portfolio.route('/portfolio', methods=["GET", "POST"])
@login_required
def main():
    order_form = OrderForm()
    return _render_template('portfolio/main.html', order_form=order_form)

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



@portfolio.route('/portfolio/order', methods=["GET", "POST"])
@login_required
@error_500_handler
def order():
    order_form = OrderForm()
    if request.method == 'POST':
        #manually input correct order_type here 
        form_data = json.loads(request.data)

        order_form.order_type.data = form_data['order_type']

        if order_form.validate_on_submit():
            ticker_name = format_ticker_name(order_form.order_ticker_name.data)
            order_type = order_form.order_type.data
            #just add entry here
            item = create_new_order_entry(ticker_name, order_form, form_type=order_type)
            ### update position entry here 
            update_position(ticker_name, item, mode=order_type)
            current_position = Position.query.filter_by(user=current_user).all()
            #update summary row - instead of creating new one, just subtract current values from deleted row and current sum row 
            return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                                summary=update_summary_row(position=current_position, ticker_item=item,
                                                        request_json=request.json, mode=order_type))        
        else:
            print(order_form.errors)
            return form_errors_400(order_form)
    else:
        redirect_next_page()


