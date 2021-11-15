from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from ..models import User
from .. import bcrypt
from .utils import username_email_query, password_check
import forex_python
from ..config import Config

class RegisterationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)],
                            render_kw={"placeholder": "Username",
                                        "id": "register-username"})
    email = StringField('Email',
                        validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Email',
                                    "id": 'register-email'})

    password = PasswordField('Password',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Password',
                            "id": "register-password"})
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')],
                                    render_kw={'placeholder': 'Confirm Password',
                                    'id': 'register-confirm-password'})
    submit = SubmitField('Create Account',
                        render_kw={'id': 'register-submit'})
    
    def validate_password(self, password):
        """custom password check to make sure theres one special symbol and one number"""
        if not password_check(password):
            raise ValidationError('Password must contain a number and a special character!')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username has already been taken!')
    
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email has already been used!')


class LoginForm(FlaskForm):
    email_username = StringField('Email_Username', 
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'Email/Username',
                                            'id': 'login-email-username'})
    password = PasswordField('Password',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Password',
                                        'id': 'login-password'})
    remember = BooleanField('Remember Me',
                            render_kw={'id': 'login-remember'})
    submit = SubmitField('Login',
                        render_kw={'id': 'login-submit'})

    def validate_password(self, password):
        """login combination check for loginform"""
        email_username = self.email_username.data
        password = password.data
        user_check = username_email_query(email_username, return_user=False)
        if not user_check:
            raise ValidationError('Invalid email/username and password combination. Please try again.')
        user = username_email_query(email_username, return_user=True)
        if user and bcrypt.check_password_hash(user.password, password):
            pass
        else:
            raise ValidationError('Invalid email/username and password combination. Please try again.')

class RequestResetForm(FlaskForm):
    email = StringField('Email_Username', 
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'Email',
                                            'id': 'request-reset-email'})
    submit = SubmitField('Request Password Reset',
                        render_kw={'id': 'request-reset-submit'})


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Password',
                            "id": "reset-password"})
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')],
                                    render_kw={'placeholder': 'Confirm Password',
                                    'id': 'reset-confirm-password'})
    submit = SubmitField('Reset Password',
                        render_kw={'id': 'reset-submit-password'})

    def validate_password(self, password):
        """custom password check to make sure theres one special symbol and one number"""
        if not password_check(password):
            raise ValidationError('Password must contain a number and a special character!')

    
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password',
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'Old Password',
                                'id': 'change-old-password'})
    new_password = PasswordField('New Password',
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'New Password',
                                'id': 'change-new-password'})
    confirm_password = PasswordField('Confirm New Password',
                                        validators=[DataRequired(), EqualTo('new_password')],
                                        render_kw={'placeholder': 'Confirm New Password',
                                        'id': 'change-confirm-password'})
    submit = SubmitField('Change Password',
                        render_kw={'id': 'change-submit-password'})
    
    def validate_old_password(self, old_password):
        """check that old password is equal to user password"""
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError('Incorrect Password')
    
    def validate_new_password(self, new_password):
        if not password_check(new_password):
            raise ValidationError('Password must contain a number and a special character!')


class ChangeUsernameForm(FlaskForm):
    username = StringField('New Username',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'New Username',
                            'id': 'change-username'})
    confirm_username = StringField('Confirm Username',
                                    validators=[DataRequired(), EqualTo('username')],
                                    render_kw={'placeholder': 'Confirm Username',
                                    'id': 'change-confirm-username'})
    submit = SubmitField('Change Username',
                        render_kw={'id': 'change-submit-username'})


class ChangeEmailForm(FlaskForm):
    email = StringField('New email',
                            validators=[DataRequired(), Email()],
                            render_kw={'placeholder': 'New email',
                            'id': 'change-email'})
    confirm_email = StringField('Confirm Email',
                                validators=[DataRequired(), EqualTo('email'), Email()],
                                render_kw={'placeholder': 'Confirm Email',
                                'id': 'change-confirm-email'})
    submit = SubmitField('Change Email',
                        render_kw={'id': 'change-submit-email'})


class ChangeSettingsForm(FlaskForm):
    currency = SelectField(label='Default Currency',
                        choices=Config.CURRENCIES,
                        render_kw={'id': 'change-currency'})
    
    submit = SubmitField('Change Settings',
                        render_kw={'id': 'change-settings-submit'})


