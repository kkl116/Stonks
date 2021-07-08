from flask import Blueprint, request, jsonify, url_for
from ..utils.helpers import _render_template, format_ticker_name, form_errors_400, redirect_next_page
from ..utils.table_helpers import ticker_name_to_table_items, new_item_json
from ..models import PortfolioItem
from .forms import AddForm, SellForm
from .utils import (PortfolioTable, TickerItem_Portfolio, get_unique_ticker_names,
                    get_summary_row, create_new_entry, update_summary_row)
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
        query_items = PortfolioItem.query.filter_by(user=current_user).all()
        if len(query_items) == 0:
            table = PortfolioTable(items=[get_summary_row(None, None, empty=True)])
            empty = 1
        else:
            #update porfolio stats
            table_items = ticker_name_to_table_items(get_unique_ticker_names(query_items), TickerItem_Portfolio)
            #create an empty item, then update attrs to make summary row
            table_items.append(get_summary_row(query_items, table_items))
            table = PortfolioTable(items=table_items)
            empty = 0
        
        return jsonify({'table': table, 'empty': empty})
    except Exception as e:
        return jsonify({'error': str(e)})
    


@portfolio.route('/portfolio/add', methods=["GET", "POST"])
@login_required
def add():
    add_form = AddForm()
    if request.method == 'POST':
        if add_form.validate_on_submit():
            ticker_name = format_ticker_name(add_form.ticker_name.data)
            sum_market_value = request.json['summary-market_value']
            #just add entry here
            item = create_new_entry(ticker_name, add_form)
            db.session.add(item)
            db.session.commit()
            query_items = PortfolioItem.query.filter_by(user=current_user, status='OWNED').all()
            #update summary row - instead of creating new one, just subtract current values from deleted row and current sum row 
            return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                                summary=update_summary_row(query_items=query_items, ticker_item=item, sum_market_value=sum_market_value,
                                                        mode="add"))        
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
            sum_market_value = request.json['summary-market_value']
            ticker_market_value = request.json['ticker-market_value']
            item = PortfolioItem.query.filter_by(user=current_user,
            ticker_name=del_ticker)
            ticker_currency = item.first().currency
            item.delete()
            db.session.commit()
            #update summary row 
            query_items = PortfolioItem.query.filter_by(user=current_user, status='OWNED').all()
            return new_item_json(update_summary_row(query_items=query_items,
                                                        ticker_market_value=ticker_market_value,
                                                        ticker_currency=ticker_currency,
                                                        sum_market_value=sum_market_value, mode="delete"), 
                                table_class=PortfolioTable, include_id=False)
        except Exception as e:
            return jsonify({'message': str(e)})
    return redirect_next_page()


@portfolio.route('/portfolio/sell', methods=["POST"])
@login_required
def sell():
    try:
        pass
    except Exception as e:
        pass
