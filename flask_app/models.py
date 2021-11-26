from . import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as TimedSerializer
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from sqlalchemy.orm import backref

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """static methods cant modify instnace or class state - provides a way to restrict the data
    that a method can access, primarily a way to namespace your methods"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file= db.Column(db.String(20), nullable=False, default='')
    password = db.Column(db.String(60), nullable=False)
    verified = db.Column(db.Boolean(), nullable=False, default=False)
    currency = db.Column(db.String(), nullable=False, default='GBP')

    """here lazily load b/c no need to load it unless in the watchlist page..."""
    watchlistItems = db.relationship('WatchlistItem', backref='user', lazy=True,
                                        cascade="all, delete, delete-orphan", passive_deletes=True)
    portfolioItems = db.relationship('PortfolioItem', backref='user', lazy=True,
                                cascade="all, delete, delete-orphan", passive_deletes=True)
    positions = db.relationship('Position', backref='user', lazy=True,
                                cascade='all, delete, delete-orphan', passive_deletes=True)
    alerts = db.relationship('Alert', backref='user', lazy=True,
                                cascade='all, delete, delete-orphan', passive_deletes=True)
    
    
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

#just create 1-many like post, then set on delete cascade for watchlisttickers
class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_item'
    id = db.Column(db.Integer, primary_key=True)
    ticker_name = db.Column(db.String(), unique=False, nullable=False)
    notes = db.Column(db.String(), nullable=False, default='')
    sector = db.Column(db.String(), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.today())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    tags = db.relationship('WatchlistItemTag', backref='item', lazy=True,
                                        cascade="all, delete, delete-orphan", passive_deletes=True)
    db.UniqueConstraint(user_id, ticker_name)

    def __repr__(self):
        return f"WatchlistTicker('{self.ticker_name}', '{self.date_added})"

class WatchlistItemTag(db.Model):
    __tablename = 'watchlist_tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_content = db.Column(db.String(), nullable=False)
    ticker_id = db.Column(db.Integer, db.ForeignKey('watchlist_item.id', ondelete="CASCADE"), nullable=False)
    db.UniqueConstraint(ticker_id, tag_content)
    def __repr__(self):
        return f"WatchlistItemTag('{self.tag_content}', '{self.ticker_id}')"

class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_item'
    id = db.Column(db.Integer, primary_key=True)
    ticker_name = db.Column(db.String(), unique=False, nullable=False)
    purchase_price = db.Column(db.String(), unique=False, nullable=True)
    sell_price = db.Column(db.String(), unique=False, nullable=True)
    quantity = db.Column(db.String(), nullable=False)
    currency = db.Column(db.String(), nullable=False)
    order_type = db.Column(db.String(), nullable=False, default='1')
    sector = db.Column(db.String(), nullable=False, default='')
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"PortfolioItem('{self.ticker_name}', '{self.price}', '{self.quantity}', '{self.order_type}')"

class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer, primary_key=True)
    ticker_name = db.Column(db.String(), unique=True, nullable=False)
    avg_purchase_price = db.Column(db.String(), unique=False, nullable=False)
    quantity = db.Column(db.String(), unique=False, nullable=False)
    currency = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"Position('{self.ticker_name}', '{self.avg_purchase_price}', '{self.quantity}', '{self.currency}')"

class ExchangeRate(db.Model):
    __tablename__ = 'exchange_rates'
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(), nullable=False)
    to_currency = db.Column(db.String(), nullable=False)
    rate = db.Column(db.String(), nullable=False)
    date_updated = db.Column(db.String(), nullable=False, default=str(datetime.today().date()))
    db.UniqueConstraint(from_currency, to_currency)
    
    def __repr__(self):
        return f"ExchangeRate('{self.from_currency}', '{self.to_currency}', '{self.rate}' ,'{self.date_updated}')"

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    ticker_name = db.Column(db.String(), unique=False, nullable=False)
    price_level = db.Column(db.Float(), unique=False, nullable=True)
    percentage_change = db.Column(db.Float(), unique=False, nullable=True)
    date_added = db.Column(db.DateTime, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    email_alert = db.Column(db.Boolean(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
