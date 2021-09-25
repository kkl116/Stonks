from flask import Blueprint
from ..utils.helpers import _render_template

errors = Blueprint('errors', __name__)

def error_404(e):
    return _render_template('errors/404.html')


@errors.route('/500', methods=['GET', "POST"])
def error_500():
    return _render_template('errors/500.html')
