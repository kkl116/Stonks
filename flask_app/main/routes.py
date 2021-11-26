from flask import Blueprint
from flask_login import current_user
from ..utils.helpers import _render_template

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        logged_in = 1
        username=current_user.username
    else:
        logged_in = 0
        username=None
    return _render_template('main/main.html', logged_in=logged_in, username=username)

