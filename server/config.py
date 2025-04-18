class Config:
    # SECRET_KEY should be set with os.getenv("SECRET_KEY")
    # In this project, environment variables will not be used
    SECRET_KEY = "default_secret_key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True  # Does not work with `flask run`, use `flask run --debug`
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.sqlite"
    SQLALCHEMY_ECHO = True
    # Flask-Mail configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "howitzer3761919@gmail.com"
    MAIL_PASSWORD = "ujewgxhkrhygcucw"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"
