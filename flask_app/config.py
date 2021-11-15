#code ~/.bash_profile in command line to set secret variables to os environ var
import os 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #SQLALCHEMY_DATABASE_URI = "postgres://vfwqihmaukuvny:fafc7739f3a409c0818ce50be4aeeb3c3d3c4400765d978899d173ad534b9781@ec2-79-125-30-28.eu-west-1.compute.amazonaws.com:5432/d69g00kk1p8kuk"
    #before going live remember to put caching back on
    SEND_FILE_MAX_AGE_DEFAULT = 0
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    CURRENCIES = ['ARS',
    'AUD',
    'BRL',
    'CAD',
    'CHF',
    'CLP',
    'CNY',
    'COP',
    'CZK',
    'DKK',
    'EUR',
    'GBP',
    'HKD',
    'HUF',
    'IDR',
    'ISK',
    'JPY',
    'KES',
    'KRW',
    'MXN',
    'MYR',
    'NOK',
    'NZD',
    'PHP',
    'PLN',
    'SEK',
    'SGD',
    'THB',
    'TWD',
    'USD',
    'VND',
    'ZAR']



