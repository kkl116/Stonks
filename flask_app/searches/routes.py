from flask import Blueprint, request, flash, Response
from ..utils.helpers import _render_template, redirect_next_page, check_ticker_exists
from .utils import get_hist_vol_json
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
            price_chart_json = get_hist_vol_json(q)
            return _render_template('searches/search_result.html', q=q, price_chart_json=price_chart_json)
        else:
            flash('Stock symbol entered is not valid. Please try again.', 'warning')
    return redirect_next_page()
