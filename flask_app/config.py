#code ~/.bash_profile in command line to set secret variables to os environ var
import os 
from boto.s3.connection import S3Connection

deploy = True
class Config:
    if not deploy:
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    else:
        SECRET_KEY = 'postgres://tmofaouiwoyvft:51fd170fb695ae02cbd968e278ebf2e9a1e320facfab9ff05f232201d39ed0db@ec2-52-209-134-160.eu-west-1.compute.amazonaws.com:5432/d8k4sfnbse01n1'
        SQLALCHEMY_DATABASE_URI = S3Connection(os.environ.get('SQLALCHEMY_DATABASE_URI'))
        MAIL_USERNAME = S3Connection(os.environ.get('MAIL_USERNAME'))
        MAIL_PASSWORD = S3Connection(os.environ.get('MAIL_PASSWORD'))

    #SQLALCHEMY_DATABASE_URI = "postgres://vfwqihmaukuvny:fafc7739f3a409c0818ce50be4aeeb3c3d3c4400765d978899d173ad534b9781@ec2-79-125-30-28.eu-west-1.compute.amazonaws.com:5432/d69g00kk1p8kuk"
    #before going live remember to put caching back on
    SEND_FILE_MAX_AGE_DEFAULT = 0
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True



