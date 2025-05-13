from flask import Blueprint, render_template, request, redirect, url_for, flash,current_app
from flask_login import login_required
from flask_mail import Mail, Message
from server.blueprints.user.logic import generate_reset_token, verify_reset_token
from server.utils.decorators import api_response
from server.blueprints.user.forms import (
    RegistrationForm,
    PasswordForm,
    LoginForm,
    UserInfoForm,
    ResetPasswordForm,
    ForgotPasswordForm,
)
from server.blueprints.user import logic

user_bp = Blueprint("user", __name__, template_folder="templates")
mail = Mail()


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


@user_bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    form = ResetPasswordForm()

    if request.method == "GET":
        return render_template("user/reset_password.html", form=form)

    if not form.validate_on_submit():
        flash(str(form.errors), "danger")
        return redirect(url_for("user.reset_password"))

    new_password = form.password.data
    try:
        logic.update_user(new_password=new_password)
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
        flash(str(form.errors), "danger")
        return redirect(url_for("user.update_user"))

    try:
        logic.update_user(
            form.username.data,
            form.email.data,
            form.nickname.data,
        )
        flash("User information updated successfully!", "success")
        return redirect(url_for("user.update_user"))
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("user.update_user"))


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


@user_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        from server.models import User
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(email)
            reset_url = url_for('user.reset_password', token=token, _external=True)
            msg = Message(
                subject="Password Reset Request",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email],
                body=f"To reset your password, click the following link:\n{reset_url}\n\nIf you did not request this, ignore this email."
            )
            mail.send(msg)
        flash('If this email exists, a reset link has been sent.', 'info')
        return redirect(url_for('user.forgot_password'))
    return render_template('user/forgot_password.html', form=form)

@user_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    email = verify_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('user.forgot_password'))
    if form.validate_on_submit():
        password = form.password.data
        try:
            logic.reset_user_password(email, password)
            flash('Your password has been reset.', 'success')
            return redirect(url_for('index.index'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('user.forgot_password'))
    return render_template('user/reset_password.html', form=form)