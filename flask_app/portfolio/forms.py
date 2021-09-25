from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError
from ..utils.helpers import check_ticker_exists, format_ticker_name
from datetime import datetime
from ..models import PortfolioOwnership
from flask_login import current_user


date_format = "%d-%m-%Y"


class AddForm(FlaskForm):
    ticker_name = StringField('ticker name',
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'Ticker Symbol',
                                'id': 'ticker-name'})

    quantity = StringField('quantity',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Quantity'})
    purchase_price = StringField('purchase_price',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Purchase Price',
                        'id': 'purchase-price'})


    def validate_ticker_name(self, ticker_name):
        """just check that ticker exists!"""
        ticker_name = format_ticker_name(ticker_name.data)
        exists = check_ticker_exists(ticker_name)
        if not exists:
            raise ValidationError("This ticker does not exist!")

    def validate_purchase_price(self, price):
        """simple validator to ensure that price is not negative"""
        if float(price.data) < 0:
            raise ValidationError("Purchase price cannot be negative!")
    
    def validate_quantity(self, quantity):
        if float(quantity.data) < 0:
            raise ValidationError("Quantity cannot be negative!")

class SellForm(FlaskForm):
    #ticker field is not actually displayed - but just used to store which ticker was clicked when field is shown
    ticker_name = StringField('ticker name',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Ticker Symbol',
                        'id': 'sell-ticker-name'})

    quantity = StringField('quantity',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Quantity',
                            'id': 'sell-quantity'})
    price = StringField('price',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Sell Price',
                            'id': 'sell-price'})

    #change below methods to use ownership entry
    def validate_ticker_name(self, ticker_name):
        """just check that ticker exists and that this person owns these shares"""
        ticker_name = format_ticker_name(ticker_name.data)
        exists = check_ticker_exists(ticker_name)
        if not exists:
            raise ValidationError("This ticker does not exist!")
        ownership = PortfolioOwnership.query.filter_by(ticker_name=ticker_name, user=current_user).first()
        if not ownership:
            raise ValidationError("Invalid Ticker!")
    
    def validate_quantity(self, quantity):
        """make sure that sell quantity is not greater than quantity owned"""
        #problem - how to get current ticker???
        ticker_name = format_ticker_name(self.ticker_name.data)
        ownership = PortfolioOwnership.query.filter_by(ticker_name=ticker_name, user=current_user).first()
        if ownership:
            current_shares = float(ownership.quantity)
            #function here to get all the currently holding n shares
            if int(quantity.data) > current_shares:
                raise ValidationError("You don't have that many shares!")
        else:
            raise ValidationError("Invalid Ticker!")

    def validate_price(self, price):
        """check that sell price is not negative"""
        if float(price.data) < 0:
            raise ValidationError("Sell price cannot be negative!")