from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config
from flask_mail import Mail
import os 

# if testing=True auto delete and create db if db file doesn't exist
testing = True
init_db = False

db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()

mail = Mail()

if testing and init_db:
    db_path = './sql/database.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    db.create_all()
    print('***** db file deleted and reinitialized *****')


#instead of importing app in from flask_app now from flask import current_app
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    from .accounts.routes import accounts
    from .main.routes import main 
    from .searches.routes import searches
    from .watchlist.routes import watchlist
    from .portfolio.routes import portfolio
    app.register_blueprint(accounts)
    app.register_blueprint(main)
    app.register_blueprint(searches)    
    app.register_blueprint(watchlist)
    app.register_blueprint(portfolio)

    return app 