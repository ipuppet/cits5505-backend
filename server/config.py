class Config:
    # SECRET_KEY should be set with os.getenv("SECRET_KEY")
    # In this project, environment variables will not be used
    SECRET_KEY = "a3f5c8d9e6b7a1c2d4e8f9g0h1i2j3k4"  # Replace with your secure key
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "howitzer3761919@gmail.com"
    MAIL_PASSWORD = "ujewgxhkrhygcucw"


class DevelopmentConfig(Config):
    DEBUG = True  # Does not work with `flask run`, use `flask run --debug`
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.sqlite"
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"
