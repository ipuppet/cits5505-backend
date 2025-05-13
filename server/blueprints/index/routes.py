from flask import Blueprint, render_template

from server.blueprints.user.forms import LoginForm

index_bp = Blueprint("index", __name__, template_folder="templates")


@index_bp.route("/")
def index():
    return render_template(
        "index/index.html",
        login_form=LoginForm(),
    )


@index_bp.route("/about")
def about():
    return render_template(
        "index/about.html",
        login_form=LoginForm(),
    )


@index_bp.route("/contact")
def contact():
    return render_template(
        "index/contact.html",
        login_form=LoginForm(),
    )


@index_bp.route("/privacy")
def privacy():
    return render_template(
        "index/privacy.html",
        login_form=LoginForm(),
    )


@index_bp.route("/terms")
def terms():
    return render_template(
        "index/terms.html",
        login_form=LoginForm(),
    )
