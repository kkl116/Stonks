from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config
from flask_mail import Mail
from flask_heroku import Heroku
from flask_apscheduler import APScheduler
from yfQuotes import Streamer

# if testing=True auto delete and create db if db file doesn't exist
testing = True

db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()

mail = Mail()

scheduler = APScheduler()

heroku = Heroku()

streamer = Streamer(stream_log=False)

db_path = './sql/database.db'


#instead of importing app in from flask_app now from flask import current_app
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)
    heroku.init_app(app)

    from .streaming import on_message
    streamer.on_message = on_message
    streamer.init_socket()
    streamer.init_app(app)

    from .accounts.routes import accounts
    from .main.routes import main 
    from .searches.routes import searches
    from .watchlist.routes import watchlist
    from .portfolio.routes import portfolio
    from .errors.handlers import error_404, errors
    from .alerts.routes import alerts

    app.register_blueprint(accounts)
    app.register_blueprint(main)
    app.register_blueprint(searches)    
    app.register_blueprint(watchlist)
    app.register_blueprint(portfolio)
    app.register_blueprint(errors)
    app.register_blueprint(alerts)
    app.register_error_handler(404, error_404)


    return app 
