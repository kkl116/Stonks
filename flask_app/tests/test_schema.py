#tests to test that database schema is working accordingly.
import pytest 
import os 
from flask_app import create_app, db, db_path
from datetime import datetime
from flask_app.models import User, Quote

@pytest.fixture
def my_app():
    return create_app()

@pytest.fixture 
def my_db(my_app):
    #initialise a clean db
    _db_path = 'flask_app/' + db_path
    if os.path.exists(_db_path):
        os.remove(_db_path)
    
    with my_app.app_context():
        db.create_all()
    return db


#test many to many relationship
#https://programmer.help/blogs/many-to-many-relationship-of-database-in-flask.html
@pytest.mark.schema
def test_subscriptions(my_app, my_db):
    with my_app.app_context():
        user = User(username='test', password='test', email='test@gmail.om')
        quote = Quote(ticker_name='TEST', exchange='TEST', timezone='TEST',
        current_price='TEST', change='TEST', change_percent='TEST',
        last_updated=datetime.now())
        user.subscriptions.append(quote)
        my_db.session.add(user)
        my_db.session.commit()

        assert len(Quote.query.all()[0].users) == 1
        assert len(User.query.all()[0].subscriptions) == 1

        #add another user 
        user2 = User(username='test2', password='test2', email='test2@gmail.com')
        user2.subscriptions.append(quote)
        my_db.session.add(user2)
        my_db.session.commit()

        assert len(Quote.query.all()[0].users) == 2
        assert len(User.query.all()[1].subscriptions) == 1

        #delete user 1 and assert quote object is not deleted 
        my_db.session.delete(user)
        my_db.session.commit()

        assert len(Quote.query.all()) == 1
        assert len(User.query.all()) == 1


        #test deleting subscription 
        user2.subscriptions.remove(quote)
        my_db.session.commit()
        
        #quote has to be manually deleted i think...
        assert len(Quote.query.all()[0].users) == 0
        assert len(User.query.all()) == 1
        #clear db
        my_db.drop_all()

