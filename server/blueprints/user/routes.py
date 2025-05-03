from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g

from server.utils.decorators import login_required, api_response
from server.blueprints.user.forms import (
    RegistrationForm,
    PasswordForm,
    LoginForm,
    UserInfoForm,
)
import server.blueprints.user.logic as user_logic

user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        flash(form.errors, "danger")
        return redirect(url_for("index.index"))

    email = form.email.data
    password = form.password.data
    remember_me = form.remember_me.data
    try:
        user = user_logic.login(email, password)
        flash("Login successful!", "success")
        session["user_id"] = user.id
        if remember_me:
            session.permanent = True
        return redirect(url_for("dashboard.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("index.index"))


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
    nickname = form.nickname.data
    date_of_birth = form.date_of_birth.data
    sex = form.sex.data

    try:
        user_logic.register(username, password, email, nickname, date_of_birth=date_of_birth,
                            sex=sex
                            )
        flash(f"Registration successful {nickname}!", "success")
        return redirect(url_for("index.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.register"))


@user_bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    form = PasswordForm()

    if request.method == "GET":
        return render_template("user/reset_password.html", form=form)

    if not form.validate_on_submit():
        flash(form.errors, "danger")
        return redirect(url_for("user.reset_password"))

    user_id = session.get("user_id")
    new_password = form.password.data
    try:
        user_logic.reset_password(user_id, new_password)
        flash(
            "Password reset successful! Please log in with your new password.",
            "success",
        )
        return logout()
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.reset_password"))


@user_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = UserInfoForm()
    if request.method == "GET":
        return render_template("user/index.html", form=form)

    if not form.validate_on_submit():
        flash(form.errors, "danger")
        return redirect(url_for("user.update_user"))

    user_id = session.get("user_id")
    username = form.username.data
    email = form.email.data
    nickname = form.nickname.data

    try:
        user_logic.update_user(user_id, username, email, nickname)
        flash("User information updated successfully!", "success")
        return redirect(url_for("dashboard.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.update_user"))


@user_bp.route("/<string:username>")
@login_required
@api_response
def search_user(username):
    return user_logic.search_user(username)


@user_bp.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if file and file.filename:
        try:
            user_logic.update_avatar(file)
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("dashboard.index"))
        flash("Avatar updated!", "success")
    else:
        flash("No file selected.", "danger")
    return redirect(url_for("dashboard.index"))
