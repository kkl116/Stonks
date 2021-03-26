import os 
import secrets 
from PIL import Image
#import models 
#import forms
from flask_app import app, db, bcyrpt
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, abort, Response
from utils import data_funcs

test = True

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    q = request.args.get('q')
    if q:
        #put in a check here to check that stock is valid and time check (if premarket/afterhours redirect to somewhere else)
        if data_funcs.check_ticker_exists(q):
            #SSE
            quote_route = '/_live-quote-' + q
            _r = _live_quote_data(q) #create a Response engine for the quote here
            prev_close = _previous_close(q)
            return render_template('search_result.html', quote_route=quote_route, q=q, prev_close=prev_close)
        else:
            flash('Stock symbol entered is not valid. Please try again.', 'warning')
    return render_template('index.html')

@app.route('/_live-quote-<q>')
def _live_quote_data(q):
    return Response(data_funcs.get_live_quotes(q, test=test), mimetype='text/event-stream')

#don't need to create a page for it I guess 
def _previous_close(q):
    return data_funcs.get_previous_close(q, test=test)

