import os 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

# if testing=True auto delete and create db if db file doesn't exist
testing = True
init_db = False

app = Flask(__name__)
app.config['SECRET_KEY'] = '0ba55d18c09b32a748964a763847445d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./sql/database.db'
#before going live remember to put caching back on
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

if testing and init_db:
    db_path = './sql/database.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    db.create_all()
    print('***** db file deleted and reinitialized *****')

from flask_app import routes