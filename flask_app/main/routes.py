from flask import Blueprint
from ..utils.helpers import _render_template

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
    return _render_template('main/main.html')