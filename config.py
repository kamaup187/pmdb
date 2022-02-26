import os
# basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'thisisjustarandomkeyforkiota'


class ProductionConfig(Config):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = os.environ['HEROKU_POSTGRESQL_AQUA_URL']
    SQLALCHEMY_DATABASE_URI = os.getenv('HEROKU_POSTGRESQL_AQUA_URL')


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL')

configurations = {
    "development":DevelopmentConfig,
    "staging":StagingConfig,
    "production":ProductionConfig,
    "testing":TestingConfig
}