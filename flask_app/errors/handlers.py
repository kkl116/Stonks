from flask import Blueprint
from ..utils.helpers import _render_template

errors = Blueprint('errors', __name__)

def error_404(e):
    """functions as an error handler for 404"""
    return _render_template('errors/404.html')

@errors.route('/500', methods=["GET", "POST"])
def error_500():
    """functions primarily as a ROUTE that js redirects to when 500 status code encountered"""
    return _render_template('errors/500.html')
