import os 
from flask_app import create_app, db, bcrypt
from flask_app.models import User

if __name__ == '__main__':
    #check if db file already exists
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    db_uri = os.path.join('flask_app', db_uri.split('///')[-1][2:])
    print(db_uri)
    if os.path.exists(db_uri):
        os.remove(db_uri)
        print('db deleted')

    app = create_app()
    db.init_app(app)
    with app.app_context():
        db.create_all()

    #add a dummy user 
    with app.app_context():
        password='abcd!234'
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username='test', password=hashed_password, email='bibstonkspage@gmail.com', verified=True)
        db.session.add(user)
        db.session.commit()
