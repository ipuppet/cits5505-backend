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
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.config.from_pyfile("config.py", silent=True)
    
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
  


    # Register the blueprints
    from server.blueprints.index.routes import index_bp
    from server.blueprints.user.routes import user_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp, url_prefix="/user")

    return app
