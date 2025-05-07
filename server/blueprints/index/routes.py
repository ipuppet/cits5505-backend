from flask import Blueprint, render_template

from server.blueprints.user.forms import LoginForm

index_bp = Blueprint("index", __name__, template_folder="templates")


@index_bp.route("/")
def index():
    login_form = LoginForm()
    return render_template("index/index.html", login_form=login_form)
