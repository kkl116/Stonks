from ..models import User
from .. import mail
from flask_mail import Message
from flask import url_for, jsonify
from string import punctuation, digits

def username_email_query(email_username_data, User=User, return_user=True):
    user = [User.query.filter_by(email=email_username_data).first(), User.query.filter_by(username=email_username_data).first()]
    user = [u for u in user if u is not None]
    if len(user) > 0:
        if return_user:
            return user[0]
        else:
            return True
    else:
        if return_user:
            return None
        else:
            return False

def send_reset_email(user):
    """external returns absolute vs relative url"""
    token = user.get_reset_token(expires_sec=84600)
    msg = Message('Password Reset Request', sender='noreply@bibstonks.com',
                recipients=[user.email])
    msg.body = f'''To reset your password, please visit the following link:

    {url_for('accounts.reset_password', token=token, _external=True)}
    
    If you did not make this request please ignore this email! :)
    '''
    mail.send(msg)

def send_verification_email(user):
    """send email to verify email is realllll"""
    token = user.get_verification_token()
    msg = Message('Account activation - Bib Stonks', sender='noreply@bibstonks.com',
                recipients=[user.email])
    msg.body = f""" To activate your account, please visit the following link:

    {url_for('accounts.email_verification', token=token, _external=True)}

    If you did not register an account with Bib Stonks, please ignore this email! :)
    """
    mail.send(msg)

def account_is_activated(login_form):
    user = username_email_query(login_form.email_username.data, return_user=True)
    return user.verified

def password_check(password):
    numbers = digits
    symbols = set(punctuation)
    number_check = False 
    symbol_check = False 
    for char in password.data:
        if char in numbers:
            number_check = True 
        elif char in symbols: 
            symbol_check = True 
    if not number_check or not symbol_check:
        return False
    else:
        return True

def redirect_json(route='main.home'):
    return jsonify({"redirect": url_for(route)})

def form_errors_400(form):
    return jsonify(form.errors), 400

