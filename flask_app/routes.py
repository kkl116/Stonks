import os 
import ast
import secrets 
from functools import wraps
from PIL import Image
from flask_app.models import User
from flask_app.forms import RegisterationForm, LoginForm
from flask_app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, Response, jsonify
from utils import data_funcs

from flask_app import testing

testing = testing

def confirm_post_request_form(request, form):
    """check that post request's fields match the registeration form
    for _render_template so that in the future other post requests can work normally.
    Expects request.form for request_data and the flaskform instance
     you're validating against"""
    form_fields = list(form._fields.keys())
    form_fields = [f for f in form_fields if f not in ['remember', 'submit']]
    form_fields.sort()
    request_data = request.decode('utf-8')
    try:
        request_data = ast.literal_eval(request_data)
    except Exception as e:
        print(e)
        return False
    request_keys = list(request_data.keys())
    request_keys = [k for k in request_keys if 'remember' != k]
    request_keys.sort()
    print(form_fields)
    print(request_keys)
    check = form_fields == request_keys
    return check


def _render_template(*args, **kwargs):
    """_render_template is for passing login and register form to all routes and processing.
    Bit of an ugly hack for the modal forms!"""
    register_form = RegisterationForm()
    login_form = LoginForm()
    kwargs['register_form'] = register_form
    kwargs['login_form'] = login_form

    return render_template(*args, **kwargs)

def render_next_page():
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('index'))

@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def index():
    q = request.args.get('q')
    if q:
        q = q.strip()
        #put in a check here to check that stock is valid and time check (if premarket/afterhours redirect to somewhere else)
        if data_funcs.check_ticker_exists(q):
            #SSE
            quote_route = '/_live-quote-' + q
            _r = _live_quote_data(q) #create a Response engine for the quote here
            prev_close = _previous_close(q)
            return _render_template('search_result.html', quote_route=quote_route, q=q, prev_close=prev_close)
        else:
            flash('Stock symbol entered is not valid. Please try again.', 'warning')
    return _render_template('index.html')

@app.route('/_live-quote-<q>')
def _live_quote_data(q):
    return Response(data_funcs.get_live_quotes(q, testing=testing), mimetype='text/event-stream')

#don't need to create a page for it I guess 
def _previous_close(q):
    return data_funcs.get_previous_close(q, testing=testing)

@app.route('/register', methods=["POST"])
def register():
    register_form = RegisterationForm()
    login_form = LoginForm()

    if request.method == "POST" and confirm_post_request_form(request.data, register_form):
        if register_form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
            user = User(username=register_form.username.data, password=hashed_password, email=register_form.email.data)
            db.session.add(user)
            db.session.commit()
            #clear form fields
            register_form.email.data = ''
            register_form.username.data = ''
            return render_next_page()
        else:
            return jsonify(register_form.errors), 400
    return render_next_page()

@app.route('/login', methods=['POST'])
def login():
    register_form = RegisterationForm()
    login_form = LoginForm()
    if request.method == "POST" and confirm_post_request_form(request.data, login_form):
        if login_form.validate_on_submit():
            print('login validated')
            user = [User.query.filter_by(email=login_form.email_username.data).first(), User.query.filter_by(username=login_form.email_username.data).first()]
            user = [u for u in user if u is not None][0]
            login_user(user, remember=login_form.remember.data)
            #just clearing form fields... but also did it in js 
            login_form.email_username.data = ''
            return render_next_page()
        else:
            print('jsonifying')
            return jsonify(login_form.errors), 400
    return render_next_page()

