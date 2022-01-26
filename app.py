from flask_app import create_app, scheduler, db, streamer
import pytest
import os

app = create_app()
ON_HEROKU = 'ON_HEROKU' in os.environ
if __name__ == '__main__':
    debug = not ON_HEROKU
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #start apscheduler
    with app.app_context():
        from flask_app.scheduled import tasks
        scheduler.start()
        if ON_HEROKU:
            db.create_all()

    #start streamer 
    streamer.connect()
    app.run(threaded=True, debug=debug)

