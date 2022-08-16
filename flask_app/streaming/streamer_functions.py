from flask_app import db, streamer
from flask_app.models import Quote
from yfQuotes.streamquotes import Decoder 
from datetime import datetime
from .classes import EventHandler

quotes_queue = EventHandler()

#functions used by streamer
def on_message(app, message):
    decoded = Decoder(message)
    ticker_name = decoded.id
    data = data_adaptor(decoded.data)

    with app.flask_app.app_context():
        update_db_quote(ticker_name, data)

    data['ticker_name'] = ticker_name
    quotes_queue.add_all(data)
    return 

def update_db_quote(ticker_name, data):
    #update quote object in database 
    quote = Quote.query.filter_by(ticker_name=ticker_name).first()
    for key, val in data.items():
        setattr(quote, key, val)
    
    quote.last_updated = datetime.now()

    streamer._logger.info(str(quote))
    db.session.commit()

#function to fix some of the fields from inbound message to match sql model fields 
def data_adaptor(data, n_places=5):
    #adjust names of fields 
    to_dict = {
    'price': 'current_price',
    'changePercent': 'change_percent',
    'change': 'change',
    'dayLow': 'day_low',
    'dayHigh': 'day_high',
    'dayVolume': 'day_volume'
    }

    #remove keys that are not in to_dict 
    remove_keys = [key for key in data.keys() if key not in to_dict.keys()]
    for key in remove_keys:
        del data[key]

    for key in to_dict:
        data[to_dict[key]] = str(round(data[key], n_places))
        if key != 'change':
            del data[key]

    return data 

#function to handle alert sse push (to watchlists and portfolios) and emails