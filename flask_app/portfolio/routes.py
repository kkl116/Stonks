from flask import Blueprint, request, jsonify
from ..utils.helpers import _render_template, format_ticker_name, form_errors_400
from ..utils.table_helpers import ticker_name_to_table_items, new_item_json
from ..models import PortfolioItem
from .forms import AddForm
from .utils import (PortfolioTable, TickerItem_Portfolio,
                    get_ticker_currency, get_unique_ticker_names,
                    get_summary_row)
from datetime import datetime
from flask_login import current_user, login_required
from flask_app import db

portfolio = Blueprint('portfolio', __name__)

@portfolio.route('/portfolio', methods=["GET", "POST"])
@login_required
def main():
    add_form = AddForm()
    #order by name right now... but later on can order by other things like value or sector etc.
    query_items = PortfolioItem.query.filter_by(user=current_user).all()
    if len(query_items) == 0:
        table = PortfolioTable(items=[TickerItem_Portfolio('empty')])
        empty = True
    else:
        #update porfolio stats
        table_items = ticker_name_to_table_items(get_unique_ticker_names(query_items), TickerItem_Portfolio)
        #create an empty item, then update attrs to make summary row
        table_items.append(get_summary_row(query_items))
        table = PortfolioTable(items=table_items)
        empty = False
        
    return _render_template('portfolio/main.html', add_form=add_form, table=table, empty=empty)

@portfolio.route('/portfolio/add', methods=["GET", "POST"])
@login_required
def add():
    add_form = AddForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            ticker_name = format_ticker_name(add_form.ticker_name.data)
            #just add entry here
            item = PortfolioItem(user=current_user,
            ticker_name=ticker_name, purchase_price=add_form.purchase_price.data,
            quantity=add_form.quantity.data, currency=get_ticker_currency(ticker_name))
            db.session.add(item)
            db.session.commit()

            return new_item_json(TickerItem_Portfolio(ticker_name), PortfolioTable, include_id=True)
        else:
            return form_errors_400(add_form)
    else:
        redirect_next_page()

@portfolio.route('/portfolio/delete', methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        try:
            del_ticker = request.json['ticker']
            item = PortfolioItem.query.filter_by(user=current_user,
            ticker_name=del_ticker).delete()
            db.session.commit()
            return jsonify({'message': 'ticker has been deleted'})
        except Exception as e:
            return jsonify({'message': str(e)})
    return redirect_next_page()


