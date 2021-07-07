from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError
from ..utils.helpers import check_ticker_exists, format_ticker_name
from datetime import datetime
from ..models import WatchlistItem
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
    sell_price = StringField('price',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Sell Price',
                            'id': 'sell-price'})

    def validate_ticker_name(self, ticker_name):
        """just check that ticker exists!"""
        ticker_name = format_ticker_name(ticker_name.data)
        exists = check_ticker_exists(ticker_name)
        if not exists:
            raise ValidationError("This ticker does not exist! Please try again.")
    
    def validate_quantity(self, quantity):
        """make sure that sell quantity is not greater than quantity owned"""
        #problem - how to get current ticker???
        current_shares = WatchlistItem.query.filter_by(user=current_user, ticker_name=self.ticker.data).first().quantity
        if quantity.data > current_shares:
            raise ValidationError("Quantity cannot be greater than available shares!")

    def validate_sell_price(self, price):
        """check that sell price is not negative"""
        if float(price.data) < 0:
            raise ValidationError("Sell price cannot be negative!")