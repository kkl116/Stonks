import os 
from flask_app import create_app, db, bcrypt
from flask_app.portfolio.utils import get_ticker_info
from flask_app.models import User, WatchlistItem, PortfolioItem
from flask_app.watchlist.utils import get_sector

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
        #with app.app_context():
        #    user = User.query.filter_by(username=test_username).first()
        #    watchlist = WatchlistItem.query.filter_by(user=user).all()
        os.remove(db_uri)
        print('db deleted')


    with app.app_context():
        db.create_all()

    #portfolio items to be added when init
    # portfolio_dict = {
    #     'GME': ['244.09', '40'],
    #     'ROO.L': ['390', '256'],
    #     'MRNA': ['402.64', '10'],
    #     'OTLY': ['28.79', '25']
    # }
    #sold ford 100 shares at 15.53
    portfolio_dict = 0

    watchlist = [
        'GME', 'PLTR', 'NVDA', 'ROO.L', 'MMED.NE', 'ETH-USD',
        #'HBAR-USD', 'DOGE-USD', 'BTC-USD', 'CTXR', 'F', 'AMC',
        'BB', 'CTXR', 'MRNA', 'BNTX', 'AMC', 'HBAR-USD',
        'OTLY', '^VIX', 'SPY'
    ]

    #add a dummy user 
    with app.app_context():
        if clear_database:
            hashed_password = bcrypt.generate_password_hash(test_password).decode('utf-8')
            user = User(username=test_username, password=hashed_password, email=test_email, verified=True)
            db.session.add_all([user])
            db.session.commit()
            #commit all the watchlist items and portfolio items 
            watchlist_items = [WatchlistItem(ticker_name=ticker_name, user=user, sector=get_sector(ticker_name)) for ticker_name in watchlist]
            #add portfolio items here as well - 
            portfolio_items = []
            if portfolio_dict:
                for ticker_name, details in portfolio_dict.items():
                    ticker_info = get_ticker_info(ticker_name)
                    args_dict = {'user': user,
                    'ticker_name': ticker_name,
                    'price': details[0],
                    'quantity': details[1],
                    'currency': ticker_info['currency'],
                    'sector': ticker_info['sector'],
                    'order_type': '1'}
                    portfolio_items.append(PortfolioItem(**args_dict))

            db.session.add_all(portfolio_items)
            db.session.add_all(watchlist_items)
            db.session.commit()
            print('db reinitialized')
