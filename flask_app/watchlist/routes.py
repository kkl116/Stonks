from flask import Blueprint, request, jsonify, Response
from flask_app.utils.helpers import (_render_template, confirm_post_request_form, redirect_json, 
                            redirect_next_page, format_ticker_name, unsubscribe_user)
from flask_app.errors.utils import error_500_handler, form_errors_400
from .utils import (WatchlistTable, TickerItem_Watchlist, get_notes_tr,
                    create_new_tag_entry, span_from_tag_item,
                    get_sector_btn, watchlist_add_item)
from flask_app.utils.table_helpers import new_item_json, query_to_table_items
from flask_app.utils.helpers import get_quote_object
from flask_login import login_required, current_user
from .forms import AddForm
from flask_app.models import WatchlistItem, WatchlistItemTag, User
from flask_app import db
from flask_app.streaming import quotes_queue
from flask_app.streaming.classes import SSEMessage

watchlist = Blueprint('watchlist', __name__)

@watchlist.route('/watchlist', methods=["GET", "POST"])
@login_required
def main():
    add_form = AddForm()
    return _render_template('watchlist/main.html', add_form=add_form)


@watchlist.route('/watchlist/get_table', methods=["GET", "POST"])
@login_required
@error_500_handler
def get_table():
    #probably better to paginate here or else loading is really slow b/c calling to yfinance many times - 
    query_items = WatchlistItem.query.filter_by(user=current_user).order_by(WatchlistItem.date_added.desc()).all()
    if len(query_items) == 0:
        table = WatchlistTable(items=[TickerItem_Watchlist('empty')])
        empty = 1
    else:
        table_items = query_to_table_items(query_items, TickerItem_Watchlist)
        table = WatchlistTable(items=table_items)
        empty = 0
    
    return jsonify({'table': table, 'empty': empty})
    

@watchlist.route('/watchlist/add', methods=["GET", "POST"])
@login_required
@error_500_handler
def add():
    add_form = AddForm()
    if request.method == 'POST' and confirm_post_request_form(request, add_form):
        if add_form.validate_on_submit():
            #need to add the watchlist item into the db
            ticker_name = format_ticker_name(add_form.ticker_name.data)
            watchlist_add_item(ticker_name, user_id=current_user.get_id())
            return new_item_json(TickerItem_Watchlist(ticker_name), table_class=WatchlistTable, include_id=False)
        else:
            return form_errors_400(add_form)
    else:
        return redirect_next_page()

    
@watchlist.route('/watchlist/delete', methods=["POST"])
@login_required
@error_500_handler
def delete():
    del_ticker = request.json['ticker']
    item = WatchlistItem.query.filter_by(user=current_user, ticker_name=del_ticker).first()
    db.session.delete(item)
    db.session.commit()
    #remove relationship from current user 
    quote = get_quote_object(del_ticker)
    user = User.query.get(current_user.get_id())
    #but what if it's still in portfolio? then shouldn't just remove subscription willy nilly 
    unsubscribe_user(user, quote)
    return jsonify({'message': 'ticker has been deleted'})


@watchlist.route('/watchlist/save_notes', methods=["POST"])
@login_required
@error_500_handler
def save_notes():
    ticker = request.json['ticker']
    ticker_notes = request.json['notes']
    item = WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker).first()
    item.notes = ticker_notes
    db.session.commit()
    return jsonify({'message': 'notes have been added'})


@watchlist.route('/watchlist/get_notes', methods=["POST"])
@login_required
@error_500_handler
def get_notes():
    ticker = request.json['ticker']
    notes_tr = get_notes_tr(ticker)
    return jsonify({'tr': notes_tr})


@watchlist.route('/watchlist/add_tag', methods=["POST"])
@login_required
@error_500_handler
def add_tag():
    #if received empty string do nothing
    new_tag = request.json['tag']
    ticker_name = request.json['ticker']
    #I think atm store tags as a single string 
    #separated by commas in sql database
    new_tag = new_tag.strip().upper()
    item = create_new_tag_entry(new_tag, ticker_name)
    if item is not None:
        db.session.add(item)
        db.session.commit()
        #create an element that can be inserted into the table cell
        span_element = span_from_tag_item(item)
        return jsonify({'element': span_element})


@watchlist.route('/watchlist/delete_tag', methods=["POST"])
@login_required
@error_500_handler
def delete_tag():
    tag_id = request.json['tagId']
    tag_item = WatchlistItemTag.query.get(int(tag_id))
    db.session.delete(tag_item)
    db.session.commit()
    return jsonify({'message': 'tag has been deleted'})

    
@watchlist.route('/watchlist/edit_sector', methods=["POST"])
@login_required
@error_500_handler
def edit_sector():
    ticker = request.json['ticker']
    sector = request.json['sector'].strip()
    #update sector of entry 
    item = WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker).first()
    item.sector = sector 
    db.session.commit()
    newBtn = get_sector_btn(current_user, ticker)
    return jsonify({'newBtn': newBtn})

#SSE connection here 
@watchlist.route('/watchlist/stream', methods=['GET'])
@login_required 
@error_500_handler
def stream():
    def watchlist_stream():
        quotes_queue.add_queue('watchlist')
        while True:
            #queue.Queue.get() blocks until new item is available (is async) -- GENIUS
            quote = quotes_queue.listen('watchlist')
            #check if user is subscribed to this quote 
            yield SSEMessage(data=quote, type='quote').message()
    
    return Response(watchlist_stream(), mimetype='text/event-stream')


        
            
