import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from .db import db, User

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, template_folder="../templates")
    app.config.from_mapping(
        SECRET_KEY="a3f5c8d9e6b7a1c2d4e8f9g0h1i2j3k4",  # Replace with your secure key
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'db.sqlite')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    # SECRET_KEY, JWT_SECRET_KEY should set in the instance/config.py file

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                flash("Login successful!", "success")
                session["user_id"] = user.id  # Store user ID in session

                
                return redirect(url_for("index"))
            else:
                flash("Invalid email or password.", "danger")
        return render_template("login.html")
    # Routes
    @app.route("/index")
    def index():
        if "user_id" not in session:  # Check if the user is logged in
            flash("You need to log in to access this page.", "warning")
            return redirect(url_for("login"))
        return render_template("index.html")
    
    @app.route("/logout")
    def logout():
        session.pop("user_id", None)  # Remove user ID from session
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]

            # Check if the email is already registered
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email is already registered.", "danger")
                return redirect(url_for("register"))

            # Create a new user
            new_user = User(name=name, email=email)
            new_user.set_password(password)  # Hash the password
            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    return app
    

    

# To set the FLASK_APP environment variable, run the following command in your terminal:
# export FLASK_APP=server.app  # For Linux/Mac
# set FLASK_APP=server.app     # For Windows
