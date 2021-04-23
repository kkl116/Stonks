from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from ..utils.helpers import check_ticker_exists
from ..models import WatchlistItem

class AddForm(FlaskForm):
    ticker_name = StringField('ticker name',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Add a ticker to your watchlist...',
                            'id': 'ticker-name'})
    def validate_ticker_name(self, ticker_name):
        """check that ticker exists and that it has not been added to the database by that user"""
        exists = check_ticker_exists(ticker_name.data)
        if not exists:
            raise ValidationError("This ticker does not exist! Please try again.")
        added = len(WatchlistItem.query.filter_by(user=current_user, ticker_name=ticker_name.data).all())
        if added:
            raise ValidationError("This ticker has already been added! Please try again.")



