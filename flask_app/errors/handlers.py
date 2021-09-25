from flask import Blueprint
from ..utils.helpers import _render_template

def error_404(e):
    return _render_template('errors/404.html')
