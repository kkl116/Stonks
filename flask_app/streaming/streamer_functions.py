from flask_app import db 
from flask_app.models import User, Quote

#functions to handle quote streaming 
def on_message(app, message):
    pass

#functions to handle db upon subscription and unsubscription
def subscribe(user, ticker_name):
    pass 

def unsubscribe(user, ticker_name):
    pass

#function to handle alert sse push and emails