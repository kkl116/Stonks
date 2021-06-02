from flask import Blueprint, request, jsonify, url_for
from ..utils.helpers import _render_template, format_ticker_name, form_errors_400
from ..utils.table_helpers import ticker_name_to_table_items, new_item_json
from ..models import PortfolioItem
from .forms import AddForm
from .utils import (PortfolioTable, TickerItem_Portfolio, get_unique_ticker_names,
                    get_summary_row, create_new_entry)
from datetime import datetime
from flask_login import current_user, login_required
from flask_app import db

portfolio = Blueprint('portfolio', __name__)

@portfolio.route('/portfolio/loading', methods=["GET", "POST"])
@login_required
def loading():
    url = url_for('portfolio.main')
    return _render_template('loading.html', url=url, pageName='portfolio')


@portfolio.route('/portfolio', methods=["GET", "POST"])
@login_required
def main():
    add_form = AddForm()
    #order by name right now... but later on can order by other things like value or sector etc.
    query_items = PortfolioItem.query.filter_by(user=current_user).all()
    if len(query_items) == 0:
        table = PortfolioTable(items=[get_summary_row(None, empty=True)])
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
            item = create_new_entry(ticker_name, add_form)
            db.session.add(item)
            db.session.commit()
            #update summary row 
            query_items = PortfolioItem.query.filter_by(user=current_user).all()
            return new_item_json(TickerItem_Portfolio(ticker_name), table_class=PortfolioTable, include_id=True,
                                summary=get_summary_row(query_items))
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
            #update summary row 
            query_items = PortfolioItem.query.filter_by(user=current_user).all()
            return new_item_json(get_summary_row(query_items), table_class=PortfolioTable, include_id=False)
        except Exception as e:
            return jsonify({'message': str(e)})
    return redirect_next_page()


