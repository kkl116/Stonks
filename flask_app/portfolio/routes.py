from flask import Blueprint, request, jsonify, url_for, Response, current_app
from flask_app.utils.helpers import _render_template, format_ticker_name, redirect_next_page
from flask_app.errors.utils import error_500_handler, form_errors_400
from flask_app.utils.table_helpers import query_to_table_items
from flask_app.models import Position
from .forms import OrderForm
from .utils import (PortfolioTable, TickerItem_Portfolio,
                    get_summary_row, create_new_order_entry, update_position)
from flask_login import current_user, login_required
from flask_app.streaming import quotes_queue
from flask_app.streaming.classes import SSEMessage
import json
import time

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
        print('*** empty table ***')
        table = PortfolioTable(items=[get_summary_row(None, empty=True)])
        empty = 1
    else:
        #update porfolio stats
        table_items = query_to_table_items(positions, TickerItem_Portfolio)
        #create an empty item, then update attrs to make summary row
        table_items.append(get_summary_row(table_items))
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
            return jsonify({'main_url': url_for('portfolio.main')})   
        else:
            return form_errors_400(order_form)
    else:
        redirect_next_page()


#SSE connection here 
@portfolio.route('/portfolio/stream', methods=['GET'])
@login_required 
@error_500_handler
def stream():
    #need to pass exch rate to watchlist_stream
    def watchlist_stream():
        quotes_queue.add_queue('portfolio')
        while True:
            #queue.Queue.get() blocks until new item is available (is async) -- GENIUS
            quote = quotes_queue.listen('portfolio')
            #check if user is subscribed to this quote 
            #need to add additional data here to update summary row...
            #this isn't the smartest way, but we're not dealing with a ton of data so - 
            yield SSEMessage(data=quote, type='quote').message()

    return Response(watchlist_stream(), mimetype='text/event-stream')

