from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError
from ..utils.helpers import check_ticker_exists, format_ticker_name
from datetime import datetime


date_format = "%d-%m-%Y"


class AddForm(FlaskForm):
    ticker_name = StringField('ticker name',
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'Ticker Symbol',
                                'id': 'ticker-name'})

    quantity = StringField('quantity',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Quantity'})
    purchase_price = StringField('price',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Purchase Price',
                        'id': 'purchase-price'})


    def validate_ticker_name(self, ticker_name):
        """just check that ticker exists!"""
        ticker_name = format_ticker_name(ticker_name.data)
        exists = check_ticker_exists(ticker_name)
        if not exists:
            raise ValidationError("This ticker does not exist! Please try again.")

    def validate_purchase_price(self, price):
        """simple validator to ensure that price is not negative"""
        if float(price.data) < 0:
            raise ValidationError("Purchase price cannot be negative!")
    
    def validate_quantity(self, quantity):
        if float(quantity.data) < 0:
            raise ValidationError("Quantity cannot be negative!")