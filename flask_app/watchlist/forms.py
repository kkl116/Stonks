from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from ..utils.helpers import check_ticker_exists

class WatchlistForm(FlaskForm):
    ticker_name = StringField('ticker name',
                            validators=[DataRequired()])
    ticker_notes = TextAreaField('ticker notes')

    def validate_ticker_name(self, ticker_name):
        """check that ticker exists"""
        exists = check_ticker_exists(ticker_name.data)
        if not exists:
            raise ValidationError("This ticker does not exist! Please try again.")

