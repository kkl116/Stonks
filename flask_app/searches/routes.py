from flask import Blueprint, request, flash, Response
from flask_app.utils.helpers import _render_template, render_next_page
from flask_app.searches.utils import get_live_quotes, check_ticker_exists, get_previous_close
from flask_app import testing

searches = Blueprint('searches', __name__)

@searches.route('/_live-quote-<q>')
def get_live_quote_data(q):
    return Response(get_live_quotes(q, testing=testing), mimetype='text/event-stream')

@searches.route('/search')
def search():
    q = request.args.get('q')
    if q:
        q = q.strip().upper()
        #put in a check here to check that stock is valid and time check (if premarket/afterhours redirect to somewhere else)
        if check_ticker_exists(q):
            #SSE
            quote_route = '/_live-quote-' + q
            _r = get_live_quote_data(q) #create a Response engine for the quote here
            prev_close = get_previous_close(q, testing=testing)
            print(prev_close)
            return _render_template('search_result.html', quote_route=quote_route, q=q, prev_close=prev_close)
        else:
            flash('Stock symbol entered is not valid. Please try again.', 'warning')
    return render_next_page()
