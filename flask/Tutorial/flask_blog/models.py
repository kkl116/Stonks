#primary_key indicates it is a unique id for user
#nullable means that field cannot be blank
#1-to-many relationship because User can have many relationships
#what backref does is when we have a post we can use the author attribute to backtrack to user that posted
from flask_blog import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#lazy argument defines when SQLAlchemy loads the data from database - True means SQL
#alchemy will load data when necessary

#to create db.. go to command line, run python, then run 'from flask_blog import db'
#then, db.create_all(), which will create the site.db file specified above
#db.session.add(Model instance) : adds changes to current session
#db.session.commit(): commit changes to database
#User.query.all() - shows all users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    #__repr__ is to set what is shown in running (instance)
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

#using lower case u in user.id here b/c in user model we're referencing Post class, whereas
#foreign key is referencing table and column name so it's lowercase
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

