from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from server.utils.decorators import login_required
from server.models import db, User
from server.blueprints.user.forms import RegistrationForm

user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("user/login.html")

    email = request.form["email"]
    password = request.form["password"]
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        flash("Login successful!", "success")
        session["user_id"] = user.id
        return redirect(url_for("index.index"))
    flash("Invalid email or password.", "danger")
    return render_template("user/login.html")


@user_bp.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove user ID from session
    flash("You have been logged out.", "info")
    return redirect(url_for("index.index"))


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("user/register.html", form=form)

    if not form.validate_on_submit():
        flash(form.errors, "danger")
        return redirect(url_for("user.register"))

    username = form.username.data
    password = form.password.data
    email = form.email.data
    nickname = form.nickname.data or username

    # Check if the username or email already exists
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        flash("Username or email already exists.", "danger")
        return redirect(url_for("user.register"))

    # Create a new user
    try:
        new_user = User(
            username=username,
            nickname=nickname,
            password=User.hash_password(password),  # Hash the password
            email=email,
        )
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        flash("Registration failed. Please try again.", "danger")
        return redirect(url_for("user.register"))

    flash(f"Registration successful {nickname}! You can now log in.", "success")
    return redirect(url_for("user.login"))


@user_bp.route("/<int:user_id>")
@login_required
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("index"))
    # TODO Render user profile page
    return f"User Info: {user}"
