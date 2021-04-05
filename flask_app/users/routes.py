from flask import Blueprint, jsonify, request
from flask_app.users.forms import LoginForm, RegisterationForm
from flask_app.models import User
from flask_app import db, bcrypt
from flask_app.utils.helpers import render_next_page, confirm_post_request_form
from flask_login import login_user

users = Blueprint('users', __name__)

@users.route('/register', methods=["POST"])
def register():
    register_form = RegisterationForm()
    login_form = LoginForm()

    if request.method == "POST"  and confirm_post_request_form(request, register_form):
        print('is register form')
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

@users.route('/login', methods=['POST'])
def login():
    register_form = RegisterationForm()
    login_form = LoginForm()
    if request.method == "POST" and confirm_post_request_form(request, login_form):
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

#need to do logout route and email reset.