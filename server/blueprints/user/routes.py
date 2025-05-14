from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from server.utils.decorators import api_response
from server.blueprints.user.forms import (
    RegistrationForm,
    PasswordForm,
    LoginForm,
    UserInfoForm,
    ForgotPasswordForm,
)
from server.blueprints.user import logic

user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = UserInfoForm()
    if request.method == "GET":
        return render_template("user/index.html", form=form)

    if not form.validate_on_submit():
        flash(str(form.errors), "danger")
        return redirect(url_for("user.index"))

    try:
        logic.update_user(
            form.username.data,
            form.email.data,
            form.nickname.data,
        )
        flash("User information updated successfully!", "success")
        return redirect(url_for("user.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.index"))


@user_bp.route("/login", methods=["POST"])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        flash(str(form.errors), "danger")
        return redirect(url_for("index.index"))

    try:
        logic.login(
            form.email.data,
            form.password.data,
            form.remember_me.data,
        )
        flash("Login successful!", "success")
        return redirect(url_for("dashboard.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("index.index"))


@user_bp.route("/logout")
def logout():
    logic.logout()
    flash("You have been logged out.", "success")
    return redirect(url_for("index.index"))


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if request.method == "GET":
        return render_template("user/register.html", form=form)

    if not form.validate_on_submit():
        flash(str(form.errors), "danger")
        return redirect(url_for("user.register"))

    try:
        logic.create_user(
            form.username.data,
            form.password.data,
            form.email.data,
            form.nickname.data,
            date_of_birth=form.date_of_birth.data,
            sex=form.sex.data,
        )
        flash(f"Registration successful {form.nickname.data}!", "success")
        return redirect(url_for("index.index"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.register"))


@user_bp.route("/password/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = PasswordForm()
    if request.method == "GET":
        return render_template("user/reset_password.html", form=form)

    if not form.validate_on_submit():
        flash(str(form.errors), "danger")
        return redirect(url_for("user.reset_password"))

    try:
        logic.reset_password(token, form.password.data)
        flash(
            "Password reset successful! Please log in with your new password.",
            "success",
        )
        return logout()
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.reset_password"))


@user_bp.route("/password/forgot", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            logic.send_reset_email(email)
            flash("If this email exists, a reset link has been sent.", "info")
            return redirect(url_for("user.forgot_password"))
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("user.forgot_password"))

    return render_template("user/forgot_password.html", form=form)


@user_bp.route("/<string:username>")
@login_required
@api_response
def search_user(username):
    return logic.search_user(username)


@user_bp.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if file and file.filename:
        try:
            logic.update_avatar(file)
        except Exception as e:
            flash(str(e), "danger")
            return redirect(url_for("dashboard.index"))
        flash("Avatar updated!", "success")
    else:
        flash("No file selected.", "danger")
    return redirect(url_for("dashboard.index"))
