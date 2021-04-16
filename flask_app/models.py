from flask_app import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """static methods cant modify instnace or class state - provides a way to restrict the data
    that a method can access, primarily a way to namespace your methods"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file= db.Column(db.String(20), nullable=False, default='static/assets/doglion_real.png')
    password = db.Column(db.String(60), nullable=False)
    verified = db.Column(db.Boolean(), nullable=False, default=False)
    
    def get_reset_token(self, expires_sec=1800):
        s = TimedSerializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_verification_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token, timed=False):
        if timed:
            s = TimedSerializer(current_app.config['SECRET_KEY'])
        else:
            s = Serializer(current_app.config['SECRET_KEY'])
        
        try:
            user_id = s.loads(token)['user_id']
        except Exception as e:
            return None
            
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
