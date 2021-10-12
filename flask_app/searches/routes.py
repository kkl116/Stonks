from flask import Blueprint, request, flash, Response, jsonify
from ..utils.helpers import _render_template, redirect_next_page, check_ticker_exists
from ..errors.utils import error_500_handler, error_500_response
from .utils import get_hist_vol_json, get_dropdown_items, get_chart_json
from .. import testing

searches = Blueprint('searches', __name__)

@searches.route('/search')
def search():
    q = request.args.get('q')
    if q:
        q = q.strip().upper()
        #put in a check here to check that stock is valid and time check (if premarket/afterhours redirect to somewhere else)
        if check_ticker_exists(q):
            #SSE
            try:
                price_chart_json = get_hist_vol_json(q)
                dropdowns = get_dropdown_items()
                return _render_template('searches/main.html', q=q, price_chart_json=price_chart_json, dropdowns=dropdowns)
            except Exception as e:
                return error_500_response(e)
        else:
            flash('Stock symbol entered is not valid. Please try again.', 'warning')
    return redirect_next_page()

@searches.route('/search/<q>')
@error_500_handler
def search_redirect(q):
    q = q.strip().upper()
    price_chart_json = get_hist_vol_json(q)
    dropdowns = get_dropdown_items()
    return _render_template('searches/main.html', q=q, price_chart_json=price_chart_json, dropdowns=dropdowns)


@searches.route('/add_chart', methods=["POST"])
@error_500_handler
def add_chart():
    item = request.json['addItem']
    ticker = request.json['ticker']
    json = get_chart_json(ticker, item)
    return json

