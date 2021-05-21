from flask import Blueprint, request, jsonify
from ..utils.helpers import _render_template, format_ticker_name, form_errors_400
from ..utils.table_helpers import query_to_table_items, new_item_json
from ..models import PortfolioItem, Portfolio
from .forms import AddForm
from .utils import (PortfolioTable, TickerItem_Portfolio, 
                    get_portfolio_items, get_user_portfolio,
                    get_ticker_currency, add_update_portfolio)
from datetime import datetime
from flask_login import current_user, login_required
from flask_app import db

portfolio = Blueprint('portfolio', __name__)

@portfolio.route('/portfolio', methods=["GET", "POST"])
@login_required
def main():
    add_form = AddForm()
    #order by name right now... but later on can order by other things like value or sector etc.
    #do a little updating for portfolio stats here as well
    query_items = get_portfolio_items({'user': current_user})
    if len(query_items) == 0:
        table = PortfolioTable(items=[TickerItem_Portfolio('empty')])
        empty = True
    else:
        table_items = query_to_table_items(query_items, TickerItem_Portfolio)
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
            #If ticker exists, then simply change the current ticker's entry!
            item = add_update_portfolio(add_form, ticker_name)
            #return new_item_json or no? b/c if updating table then not inserting a new row
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
            item = PortfolioItem.query.filter_by(portfolio=get_user_portfolio(current_user),
            ticker_name=del_ticker).first()
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': 'ticker has been deleted'})
        except Exception as e:
            return jsonify({'message': str(e)})
    return redirect_next_page()
