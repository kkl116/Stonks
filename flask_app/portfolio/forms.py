from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError
from ..utils.helpers import check_ticker_exists, format_ticker_name
from datetime import datetime
from ..models import Position
from flask_login import current_user


date_format = "%d-%m-%Y"

def float_check(data):
    try:
        data = float(data)
    except:
        raise ValidationError("Invalid number.")
    
    return data


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
        #check that it's a number
        price = float_check(price.data)

        if price < 0:
            raise ValidationError("Purchase price cannot be negative!")
    
    def validate_quantity(self, quantity):
        quantity = float_check(quantity.data)

        if quantity < 0:
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

    def validate_ticker_name(self, ticker_name):
        """just check that ticker exists and that this person owns these shares"""
        ticker_name = format_ticker_name(ticker_name.data)
        exists = check_ticker_exists(ticker_name)
        if not exists:
            raise ValidationError("This ticker does not exist!")
        position = Position.query.filter_by(ticker_name=ticker_name, user=current_user).first()
        if not position:
            raise ValidationError("Invalid Ticker!")
    
    def validate_quantity(self, quantity):
        """make sure that sell quantity is not greater than quantity owned"""
        #problem - how to get current ticker???
        quantity = float_check(quantity.data)

        ticker_name = format_ticker_name(self.ticker_name.data)
        position = Position.query.filter_by(ticker_name=ticker_name, user=current_user).first()
        if position:
            current_shares = float(position.quantity)
            #function here to get all the currently holding n shares
            if quantity > current_shares:
                raise ValidationError("You don't have that many shares!")
        else:
            raise ValidationError("Invalid Ticker!")

    def validate_price(self, price):
        """check that sell price is not negative"""
        price = float_check(price.data)

        if price < 0:
            raise ValidationError("Sell price cannot be negative!")