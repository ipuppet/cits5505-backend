import os

from sqlalchemy.pool import NullPool


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask-Mail configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True  # Does not work with `flask run`, use `flask run --debug`
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.sqlite"
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"


class TestingConfig(Config):
    TESTING = True
    SERVER_NAME = "localhost"
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,  # Disable connection pooling
        "connect_args": {"check_same_thread": False},  # SQLite Allow across threads
    }
