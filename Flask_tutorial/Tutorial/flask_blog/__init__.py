from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
#secret key want to be random characters
app.config['SECRET_KEY'] = '7b357affc9186198889a2318d5622314'
#/// means relative path, so file should be created within project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#__name__ means just name of module 
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flask_blog import routes