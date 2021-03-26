from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = '0ba55d18c09b32a748964a763847445d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sql/site.db'
#before going live remember to put caching back on
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)
bcyrpt = Bcrypt(app)

#login_manager = LoginManager(app)
#login_manager.login_view = 'login'
#login_manager.login_message_category = 'info'

from flask_app import routes