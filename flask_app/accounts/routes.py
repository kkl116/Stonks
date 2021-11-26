from flask import Blueprint, jsonify, request, flash, redirect, url_for
from .forms import (LoginForm, RegisterationForm, 
                    RequestResetForm, ResetPasswordForm,
                    ChangePasswordForm, ChangeUsernameForm,
                    ChangeEmailForm, ChangeSettingsForm)
from ..models import User
from .. import db, bcrypt, login_manager
from ..utils.helpers import (redirect_next_page, confirm_post_request_form, _render_template, 
                            redirect_json)
from ..errors.utils import form_errors_400
from flask_login import login_user, logout_user, login_required, current_user
from .utils import (username_email_query, send_reset_email, 
                    send_verification_email, account_is_activated)

accounts = Blueprint('accounts', __name__)

@accounts.route('/register', methods=["POST", 'GET'])
def register():
    register_form = RegisterationForm()
    if request.method == "POST"  and confirm_post_request_form(request, register_form):
        if register_form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
            user = User(username=register_form.username.data, password=hashed_password, email=register_form.email.data)
            #add email verification here 
            db.session.add(user)
            db.session.commit()
            send_verification_email(user)
            #clear form fields
            flash('Your account has been created! Please activate your account before logging in.', 'success')
            return redirect_json(route="main.home")
        else:
            print(register_form.errors)
            return form_errors_400(register_form)
    return redirect_next_page()

@accounts.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    login_form = LoginForm()
    if request.method == "POST" and confirm_post_request_form(request, login_form):
        if login_form.validate_on_submit() and account_is_activated(login_form):
            print('login validated')
            user = username_email_query(login_form.email_username.data, return_user=True)
            login_user(user, remember=login_form.remember.data)
            flash('You have logged in successfully!', 'success')
            return redirect_json(route="main.home")
        else:
            return form_errors_400(login_form)
    return redirect_next_page()

@accounts.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out!', 'success')
    return redirect_next_page()

#need email reset.
@accounts.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    request_reset_form = RequestResetForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == "POST" and confirm_post_request_form(request, request_reset_form):
        #need to pass in forms to _render_template
        if request_reset_form.validate_on_submit():
            user = username_email_query(request_reset_form.email.data, return_user=True)
            if user:
                send_reset_email(user)
            return jsonify({'message': 'done!'})
        else:
            return form_errors_400(request_reset_form)
    return redirect_next_page()

@accounts.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_token(token, timed=True)
    if user is None:
        flash('The token is invalid or has expired.', 'warning')
        return redirect_next_page()

    reset_password_form = ResetPasswordForm()
    if request.method == "POST":
        if reset_password_form.validate_on_submit():
            print('reset form submitted')
            hashed_password = bcrypt.generate_password_hash(reset_password_form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Password has been updated!', 'success')
            #redirect does not work with ajax, so instead return json then use js to switch url
            return redirect_json(route="main.home")
        else:
            return form_errors_400(reset_password_form)
    return _render_template('accounts/reset_password.html')


@accounts.route('/email_verification/<token>', methods=["GET", "POST"])
def email_verification(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_token(token, timed=False)
    if user is None:
        flash('The token is invalid.', 'warning')
        return redirect_next_page()
    #submit user details to db 
    user.verified = True
    db.session.commit()
    #make a account activated page
    return _render_template('accounts/account_activated.html')

@login_manager.unauthorized_handler
def require_login():
    return _render_template('accounts/require_login.html')

@login_required
@accounts.route('/settings', methods=['GET'])
def settings():
    #settings should include ability to change password, change username, change email, alert settings, and change default currency
    changePasswordForm = ChangePasswordForm()
    changeEmailForm = ChangeEmailForm()
    changeUsernameForm = ChangeUsernameForm()
    changeSettingsForm = ChangeSettingsForm()
    changeSettingsForm.currency.data = current_user.currency
    
    return _render_template('accounts/settings.html', changePasswordForm=changePasswordForm,
                            changeEmailForm=changeEmailForm, changeUsernameForm=changeUsernameForm,
                            changeSettingsForm=changeSettingsForm)


@login_required
@accounts.route('/settings/change_password', methods=['POST'])
def change_password():
    #change password 
    changePasswordForm = ChangePasswordForm()
    changePasswordForm.validate()
    errors = changePasswordForm.errors
    if len(errors) == 0:
        #change user password 
        hashed_password = bcrypt.generate_password_hash(changePasswordForm.new_password.data).decode('utf-8')
        current_user.password = hashed_password 
        db.session.commit()
        flash('Your password has been changed!', 'success')
        return redirect_json(route='accounts.settings')
    else:
        return form_errors_400(changePasswordForm)

@login_required
@accounts.route('/settings/change_username', methods=['POST'])
def change_username():
    changeUsernameForm = ChangeUsernameForm()
    changeUsernameForm.validate()
    errors = changeUsernameForm.errors
    if len(errors) == 0:
        current_user.username = changeUsernameForm.username.data
        db.session.commit()
        flash('Your Username has been changed!', 'success')
        return redirect_json(route='accounts.settings')
    else:
        return form_errors_400(changeUsernameForm)

@login_required
@accounts.route('/settings/change_email', methods=['POST'])
def change_email():
    changeEmailForm = ChangeEmailForm()
    changeEmailForm.validate()
    errors = changeEmailForm.errors
    if len(errors) == 0:
        current_user.email = changeEmailForm.email.data
        db.session.commit()
        flash('Your Email has been changed!', 'success')
        return redirect_json(route='accounts.settings')
    else:
        return form_errors_400(changeEmailForm)

@login_required
@accounts.route('/settings/change_settings', methods=['POST'])
def change_settings():
    changeSettingsForm = ChangeSettingsForm()
    changeSettingsForm.validate()
    errors = changeSettingsForm.errors
    if len(errors) == 0:
        current_user.currency = changeSettingsForm.currency.data
        db.session.commit()
        flash('Your settings has been changed!', 'success')
        return redirect_json(route='accounts.settings')
    else:
        return form_errors_400(changeSettingsForm)