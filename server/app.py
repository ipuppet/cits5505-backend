import os
from flask import Flask

from server.models import db

from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message
import jwt
from datetime import datetime, timedelta




mail = Mail()
def create_app(config_class="server.config.DevelopmentConfig"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder="../templates")
    app.config.from_mapping(
        SECRET_KEY="a3f5c8d9e6b7a1c2d4e8f9g0h1i2j3k4",  # Replace with your secure key
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'db.sqlite')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAIL_SERVER="smtp.gmail.com",  # Gmail 
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME="howitzer3761919@gmail.com", 
        MAIL_PASSWORD="ujewgxhkrhygcucw",  
    )
    
    mail.init_app(app)

    
    # SECRET_KEY, JWT_SECRET_KEY should set in the instance/config.py file


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


    # Register the blueprints
    from server.blueprints.index.routes import index_bp
    from server.blueprints.user.routes import user_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp, url_prefix="/user")

    return app
