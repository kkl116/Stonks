#code ~/.bash_profile in command line to set secret variables to os environ var
import os 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    #before going live remember to put caching back on
    SEND_FILE_MAX_AGE_DEFAULT = 0



