from flask import request, redirect, url_for, render_template, jsonify, request
from pandas import DateOffset
from flask_app.accounts.forms import (LoginForm, RegisterationForm, 
                                    RequestResetForm, ResetPasswordForm)
from flask_app.models import Quote, WatchlistItem, Position
import ast
import yfinance as yf 
from yfQuotes import get_quotes_asyncio
from datetime import datetime
from flask_app import db

def unsubscribe_user(user, quote):
    if not still_subscribe(user, quote.ticker_name):
        print(f'{user} unsubscribed from {quote.ticker_name}')
        user.subscriptions.remove(quote)

    if len(quote.users) == 0:
        db.session.delete(quote)
    db.session.commit()


def subscribe_user(user, quote):
    if quote not in user.subscriptions:
        print(f'{user} subscribed to {quote.ticker_name}')
        user.subscriptions.append(quote) 
    db.session.commit()

#need to write function that creates Quote Object if not created already
def create_quote_object(ticker_name, ticker_info=None):
    if ticker_info is None:
        ticker_info = yf.Ticker(ticker_name).info
    prices = get_quotes_asyncio([ticker_name])[0]
    quote = Quote(ticker_name=ticker_name,
                current_price=prices['current_price'],
                exchange=ticker_info['exchange'],
                timezone=ticker_info['exchangeTimezoneShortName'],
                change=prices['increase_dollars'],
                change_percent=prices['increase_percent'],
                last_updated=datetime.now())

    db.session.add(quote)
    db.session.commit()
    return quote 

def get_quote_object(ticker_name, ticker_info=None):
    #if quote already exists then just return that 
    existing = Quote.query.filter_by(ticker_name=ticker_name).first()
    if existing:
        return existing 
    else:
        return create_quote_object(ticker_name, ticker_info)

#function to check if any user portfolioitems or watchlistitems contain ticker_name 
def still_subscribe(current_user, ticker_name):
    watchlist = WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker_name).all()
    position = Position.query.filter_by(user=current_user, ticker_name=ticker_name).all()
    if len(watchlist+position):
        return True 
    else:
        return False

def get_request_form_keys(request, omit_keys = ['remember', 'submit']):
    if len(list(request.form.keys())) > 0:
        request_keys = list(request.form.keys())
        request_keys = [k for k in request_keys if k not in omit_keys]
    else:
        request_data = request.data.decode('utf-8')
        try:
            request_data = ast.literal_eval(request_data)
        except Exception as e:
            print(e)
            return False
        request_keys = list(request_data.keys())
        request_keys = [k for k in request_keys if 'remember' != k]
    return request_keys


def confirm_post_request_form(request, form):
    """check that post request's fields match the registeration form
    for _render_template so that in the future other post requests can work normally.
    Expects request.form for request_data and the flaskform instance
     you're validating against"""
    form_fields = list(form._fields.keys())
    form_fields = [f for f in form_fields if f not in ['remember', 'submit']]
    form_fields.sort()
    request_keys = get_request_form_keys(request)
    request_keys.sort()
    check = form_fields == request_keys
    return check

def _render_template(*args, **kwargs):
    """_render_template is for passing login and register form to all routes and processing.
    Bit of an ugly hack for the modal forms!"""
    register_form = RegisterationForm()
    login_form = LoginForm()
    request_reset_form = RequestResetForm()
    reset_password_form = ResetPasswordForm()
    kwargs['register_form'] = register_form
    kwargs['login_form'] = login_form
    kwargs['request_reset_form'] = request_reset_form
    kwargs['reset_password_form'] = reset_password_form

    return render_template(*args, **kwargs)

def redirect_next_page():
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('main.home'))

def check_ticker_exists(ticker, flash_msg=True):
    """takes ticker name and checks on yahoo finance to see if it exists.
    returns a boolean
    """
    try: 
        return get_quotes_asyncio([ticker])[0]
    except Exception as e:
        print(e)
        return False


def redirect_json(route=None, url=None):
    """returns the json for ajax refresh - provide one of url or route"""
    if route and url:
        raise Exception('Both route and url provided, please provide one only.')
    elif not route and not url:
        raise Exception('Neither route or url has been provided, please provide either one.')
    elif route:
        url = url_for(route)
    elif url:
        pass

    return jsonify({"redirect": url})


def format_ticker_name(ticker_name):
    return ticker_name.strip().upper()

def html_formatter(element_type, inner_html='', **kwargs):
    """function to format html so that everything is less messy
    expect element type - which is just the different tags.
    inner_html - the main content 
    **kwargs - each key word will be considered a new attr to be added - expects 
    a list of arguments to be added. because class is a reserved phrase 
    here use cls instead.
    """
    start = '<' + element_type + ' '
    attrs = []
    for attr, args in kwargs.items():
        if attr == 'cls':
            attr = 'class'
        if type(args) == list:
            args = ' '.join(args)
        attrs.append(str(attr).replace('_', '-') + "='" + args + "'")

    end = f'</{element_type}>'
    return start + ' '.join(attrs) + '>' + inner_html + end





