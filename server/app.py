import os
from flask import Flask

from server.models import db, migrate
from server.utils.mail import mail

def create_app(config_class=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # Load the default configuration
    if config_class is None:
        env = os.getenv("FLASK_ENV", "production")
        config_class = f"server.config.{env.capitalize()}Config"
    app.config.from_object(config_class)

    # Ensure the instance folder and config file exist
    try:
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
        elif not os.path.exists(os.path.join(app.instance_path, "config.py")):
            with open(os.path.join(app.instance_path, "config.py"), "w") as f:
                f.write(
                    "# This file is used to store the configuration for the Flask app instance.\n"
                    "# This file will override the default configuration in server/config.py.\n"
                    "# You can set the SECRET_KEY here.\n"
                    "# For example:\n"
                    "# SECRET_KEY = 'your_secret_key'\n"
                )
    except OSError:
        pass
    app.config.from_pyfile("config.py", silent=True)

    # Initialize the database
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()

    # Initialize Flask-Mail
    mail.init_app(app)

    # Register the blueprints
    from server.blueprints.index.routes import index_bp
    from server.blueprints.dashboard.routes import dashboard_bp
    from server.blueprints.user.routes import user_bp
    from server.blueprints.exercise.routes import exercise_bp
    from server.blueprints.share.routes import share_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(exercise_bp, url_prefix="/exercise")
    app.register_blueprint(share_bp, url_prefix="/share")

    return app
