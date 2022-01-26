from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_app.utils.helpers import check_ticker_exists, format_ticker_name
from flask_app.models import Position
from flask_login import current_user


date_format = "%d-%m-%Y"

def float_check(data):
    try:
        data = float(data)
    except:
        raise ValidationError("Invalid number.")
    
    return data


class OrderForm(FlaskForm):
    order_ticker_name = StringField('ticker name',
                                validators=[DataRequired()],
                                render_kw={'placeholder': 'Ticker Symbol',
                                'id': 'order-ticker-name'})
    order_quantity = StringField('quantity',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Quantity',
                            'id': 'order-quantity'})
    order_price = StringField('price',
                        validators=[DataRequired()],
                        render_kw={'placeholder': 'Price',
                        'id': 'order-price'})
    order_type = RadioField('order type',
    render_kw={'id': 'order-type'},
    choices=[('buy', 'Buy'), ('sell', 'Sell')], default='buy')
    submit = SubmitField()

    def validate_order_ticker_name(self, order_ticker_name):
        """just check that ticker exists!"""
        ticker_name = format_ticker_name(order_ticker_name.data)
        exists = check_ticker_exists(ticker_name, flash_msg=False)
        if not exists:
            raise ValidationError("This ticker does not exist!")

        if self.order_type.data == 'sell':
            position = Position.query.filter_by(ticker_name=ticker_name, user=current_user).first()
            if not position:
                raise ValidationError("Invalid Ticker!")

    def validate_order_price(self, order_price):
        """simple validator to ensure that price is not negative"""
        #check that it's a number
        price = float_check(order_price.data)

        if price < 0:
            raise ValidationError("Purchase price cannot be negative!")
    
    def validate_order_quantity(self, order_quantity):
        quantity = float_check(order_quantity.data)

        if quantity < 0:
            raise ValidationError("Quantity cannot be negative!")

        if self.order_type.data == 'sell':
            ticker_name = format_ticker_name(self.order_ticker_name.data)
            position = Position.query.filter_by(ticker_name=ticker_name, user=current_user).first()
            if position:
                current_shares = float(position.quantity)
                #function here to get all the currently holding n shares
                if quantity > current_shares:
                    raise ValidationError("You don't have that many shares!")


