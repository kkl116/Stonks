import os 
from flask_app import create_app, db

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

