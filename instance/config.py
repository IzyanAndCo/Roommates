import os

home_dir = os.path.expanduser("~")


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BLUEPRINTS = ['guests', 'users', 'guest_types', 'authentication']
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 1 week


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(home_dir, 'Databases/app.db')
    JWT_SECRET_KEY = 'super-secret-key'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(home_dir, 'Databases/testing_db.db')
    JWT_SECRET_KEY = 'super-secret-key'
