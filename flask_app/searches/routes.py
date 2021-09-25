from flask import Blueprint, request, flash, Response, jsonify
from ..utils.helpers import _render_template, redirect_next_page, check_ticker_exists, error_500
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
                return error_500(e)
        else:
            flash('Stock symbol entered is not valid. Please try again.', 'warning')
    return redirect_next_page()

@searches.route('/search/<q>')
def search_redirect(q):
    q = q.strip().upper()
    try:
        price_chart_json = get_hist_vol_json(q)
        dropdowns = get_dropdown_items()
        return _render_template('searches/main.html', q=q, price_chart_json=price_chart_json, dropdowns=dropdowns)
    except Exception as e:
        error_500(e)

@searches.route('/add_chart', methods=["POST"])
def add_chart():
    if request.method == "POST":
        try:
            item = request.json['addItem']
            ticker = request.json['ticker']
            json = get_chart_json(ticker, item)
            return json
        except Exception as e:
            return error_500(e)
    return redirect_next_page()