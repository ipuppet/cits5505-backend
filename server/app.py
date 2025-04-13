import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from .db import db, User
from flask_wtf import FlaskForm,CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_mail import Mail, Message
import jwt
from datetime import datetime, timedelta




mail = Mail()
def create_app(test_config=None):
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
    return app
app = create_app()

    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()  # Create an instance of the form
    if form.validate_on_submit():  # Automatically validates the form
        email = form.email.data  # Access the validated email input
        password = form.password.data  # Access the validated password input
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            flash("Login successful!", "success")
            session["user_id"] = user.id
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)
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
    
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
                # Generate a JWT token
            payload = {
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
            reset_url = url_for("reset_password", token=token, _external=True)
            
            
            msg = Message(
                "Password Reset Request",
                sender="your_email@gmail.com",
                recipients=[email],
            )
            msg.body = f"To reset your password, visit the following link: {reset_url}"
            mail.send(msg)
            flash("A password reset email has been sent to your email address.", "success")
        else:
            flash("No account found with that email address.", "danger")
    return render_template("forgot_password.html")



@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        new_password = request.form["password"]
        # Validate the token and reset the password (dummy logic here)
        flash("Your password has been reset successfully!", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", token=token)





# To set the FLASK_APP environment variable, run the following command in your terminal:
# export FLASK_APP=server.app  # For Linux/Mac
# set FLASK_APP=server.app     # For Windows
