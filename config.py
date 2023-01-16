import os

# from app.v2.views.secrets import DATABASE_URL, HEROKU_POSTGRESQL_AQUA_URL, TEST_DATABASE_URL

try:
    from do_secrets import *
except ImportError:
    SMS_USERNAME = None
    SMS_API_KEY = None
    G_ACCOUNT = None
    G_PASS = None
    
    HEROKU_POSTGRESQL_AQUA_URL = None
    DATABASE_URL = None
    TEST_DATABASE_URL = None

# basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'thisisjustarandomkeyforkiota'


class ProductionConfig(Config):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = os.environ['HEROKU_POSTGRESQL_AQUA_URL']
    dbconn = os.getenv('HEROKU_POSTGRESQL_AQUA_URL') or HEROKU_POSTGRESQL_AQUA_URL
    # print("::::::::::::::::DATABASE CONNECTED TO: >>>>>>",dbconn)
    SQLALCHEMY_DATABASE_URI = dbconn


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or DATABASE_URL


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or DATABASE_URL


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL') or TEST_DATABASE_URL

configurations = {
    "development":DevelopmentConfig,
    "staging":StagingConfig,
    "production":ProductionConfig,
    "testing":TestingConfig
}