from flask import request, redirect, url_for, render_template, jsonify, request
from ..accounts.forms import (LoginForm, RegisterationForm, 
                                    RequestResetForm, ResetPasswordForm)
import ast
import stockquotes
from ..models import PortfolioItem

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
    try: 
        stock = stockquotes.Stock(ticker)
        return True
    except Exception as e:
        print(str(e))
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





