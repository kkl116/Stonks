"""module to handle routes to alert centre and flask-sse methods"""
from flask import Blueprint, Response, jsonify
from flask_login import current_user 
from flask_app.utils.helpers import _render_template
import time 
import json 

alerts = Blueprint('alerts', __name__)

def test_message():
    time.sleep(5.0)
    return json.dumps({'a': 1, 'b': 2})

#for client to acknowledge msg receipt the message has to be of format "data: <any_data>\n\n"
#or "id: <any_id>\nevent: <any_message>\ndata: <any_data>\n\n"
@alerts.route('/alerts-stream')
def stream():
    def eventStream():
        while True:
            yield f"data: {test_message()} \n\n"
    
    return Response(eventStream(), mimetype='text/event-stream')

@alerts.route('/alerts', methods=['GET'])
def main():
    return _render_template('alerts/main.html')