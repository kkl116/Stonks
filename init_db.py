import os 
from flask_app import create_app, db, bcrypt
from flask_app.models import User, WatchlistItem, PortfolioItem, Portfolio

clear_database = True

if __name__ == '__main__':
    test_username = 'test'
    test_password = 'abcd!234'
    test_email = 'bibstonkspage@gmail.com'

    #check if db file already exists
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    db_uri = os.path.join('flask_app', db_uri.split('///')[-1][2:])

    app = create_app()
    db.init_app(app)

    #open the db and get all the existing items
    if os.path.exists(db_uri) and clear_database:
        with app.app_context():
            user = User.query.filter_by(username=test_username).first()
            watchlist = WatchlistItem.query.filter_by(user=user).all()
        os.remove(db_uri)
        print('db deleted')


    with app.app_context():
        db.create_all()

    #add a dummy user 
    with app.app_context():
        if clear_database:
            hashed_password = bcrypt.generate_password_hash(test_password).decode('utf-8')
            user = User(username=test_username, password=hashed_password, email=test_email, verified=True)
            portfolio = Portfolio(user=user)
            db.session.add_all([user, portfolio])
            db.session.commit()
            #commit all the watchlist items and portfolio items 
            watchlist_items = [WatchlistItem(ticker_name=item.ticker_name, user=user) for item in watchlist]
            #add portfolio items here as well - 
            db.session.add_all(watchlist_items)
            db.session.commit()
            print('db reinitialized')
