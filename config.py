import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # DEBUG = True
    # DEBUG_TB_INTERCEPT_REDIRECTS = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'CHANGE_ME'
    WTF_CSRF_ENABLED = True

    # email server
    MAIL_SERVER = os.environ.get('MAIL_HOSTNAME')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # administrator list
    ADMINS = ['accounts@dallasmakerspace.org'] # email from address


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
