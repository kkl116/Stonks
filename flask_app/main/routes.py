from flask import Blueprint
from flask_app.utils.helpers import _render_template

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def index():
    return _render_template('index.html')