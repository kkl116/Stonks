from flask import request, redirect, url_for, render_template, jsonify
from ..accounts.forms import (LoginForm, RegisterationForm, 
                                    RequestResetForm, ResetPasswordForm)
import requests
import ast

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

def check_ticker_exists(ticker):
    """takes ticker name and checks on yahoo finance to see if it exists.
    returns a boolean
    """
    ticker = ticker.strip().upper()
    url = f'https://uk.finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'
    page = requests.get(url)
    if page.url == url:
        return True
    else:
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


def form_errors_400(form):
    return jsonify(form.errors), 400

def format_ticker_name(ticker_name):
    return ticker_name.strip().upper()

