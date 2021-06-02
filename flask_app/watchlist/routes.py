from flask import Blueprint, request, url_for, jsonify, abort
from ..utils.helpers import (_render_template, redirect_json, form_errors_400, 
                            redirect_next_page, format_ticker_name)
from .utils import WatchlistTable, TickerItem_Watchlist, get_notes_tr
from ..utils.table_helpers import new_item_json, query_to_table_items
from flask_login import login_required, current_user
from .forms import AddForm
from ..models import WatchlistItem
from .. import db

watchlist = Blueprint('watchlist', __name__)

@watchlist.route('/watchlist/loading', methods=["GET", "POST"])
@login_required
def loading():
    url = url_for('watchlist.main')
    return _render_template('loading.html', url=url, pageName='watchlist')

@watchlist.route('/watchlist', methods=["GET", "POST"])
@login_required
def main():
    add_form = AddForm()
    #probably better to paginate here or else loading is really slow b/c calling to yfinance many times - 
    query_items = WatchlistItem.query.filter_by(user=current_user).order_by(WatchlistItem.date_added.desc()).all()
    if len(query_items) == 0:
        table = WatchlistTable(items=[TickerItem_Watchlist('empty')])
        empty = True
    else:
        table_items = query_to_table_items(query_items, TickerItem_Watchlist)
        table = WatchlistTable(items=table_items)
        empty = False
    
    return _render_template('watchlist/main.html', add_form=add_form, table=table, empty=empty)

@watchlist.route('/watchlist/add', methods=["GET", "POST"])
@login_required
def add():
    add_form = AddForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            #need to add the watchlist item into the db
            ticker_name = format_ticker_name(add_form.ticker_name.data)
            item = WatchlistItem(ticker_name=ticker_name, user=current_user)
            db.session.add(item)
            db.session.commit()
            return new_item_json(TickerItem_Watchlist(ticker_name), table_class=WatchlistTable, include_id=False)
        else:
            return form_errors_400(add_form)
    else:
        return redirect_next_page()
    
@watchlist.route('/watchlist/delete', methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        try:
            del_ticker = request.json['ticker']
            item = WatchlistItem.query.filter_by(user=current_user, ticker_name=del_ticker).first()
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': 'ticker has been deleted'})
        except Exception as e:
            return jsonify({'message': str(e)})
    return redirect_next_page()

@watchlist.route('/watchlist/save_notes', methods=["GET", "POST"])
@login_required
def save_notes():
    if request.method == "POST":
        try:
            ticker = request.json['ticker']
            ticker_notes = request.json['notes']
            item = WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker).first()
            item.notes = ticker_notes
            db.session.commit()
            return jsonify({'message': 'notes have been added'})
            
        except Exception as e:
            return jsonify({'message': str(e)})

@watchlist.route('/watchlist/get_notes', methods=["GET","POST"])
@login_required
def get_notes():
    if request.method == "POST":
        try:
            ticker = request.json['ticker']
            notes_tr = get_notes_tr(ticker)
            return jsonify({'tr': notes_tr})
        except Exception as e:
            return jsonify({'message': str(e)})
            
