from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from server.utils.decorators import login_required
from server.blueprints.user.forms import RegistrationForm
import server.blueprints.user.logic as user_logic

user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("user/login.html")

    email = request.form["email"]
    password = request.form["password"]
    try:
        user = user_logic.login(email, password)
        flash("Login successful!", "success")
        session["user_id"] = user.id
        return redirect(url_for("index.index"))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("user.login"))
    except Exception as e:
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for("user.login"))


@user_bp.route("/logout")
def logout():
    session.pop("user_id", None)  # Remove user ID from session
    flash("You have been logged out.", "success")
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

    try:
        user_logic.register(username, password, email, nickname)
        flash(f"Registration successful {nickname}! You can now log in.", "success")
        return redirect(url_for("user.login"))
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("user.register"))
    except Exception as e:
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for("user.register"))


@user_bp.route("/<int:user_id>")
@login_required
def get_user(user_id):
    try:
        user = user_logic.get_user(user_id)
        # TODO: Render user information
        return f"User Info: {user}"
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("index.index"))
    except Exception as e:
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for("index.index"))
