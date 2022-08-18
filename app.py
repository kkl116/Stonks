from flask_app import create_app, scheduler, db, streamer
from flask_app.models import User
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
        user = User.query.filter_by(username='test').first()
        if user:
            subs = [sub.ticker_name for sub in user.subscriptions]
            streamer.add(subs)

    app.run(threaded=True, debug=True)

