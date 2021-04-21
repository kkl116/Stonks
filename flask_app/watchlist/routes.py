from flask import Blueprint
from ..utils.helpers import _render_template
from .utils import Watchlist_Table
from flask_login import login_required
from .forms import WatchlistForm

watchlist = Blueprint('watchlist', __name__)


@watchlist.route('/watchlist', methods=["GET", "POST"])
@login_required
def main():
    watchlist_form = WatchlistForm()
    table = Watchlist_Table(items=[dict(TICKER='test', PRICE='test'),
                                dict(TICKER='test2', PRICE='test2')])
    return _render_template('watchlist/main.html', watchlist_form=watchlist_form, table=table)


