from flask import Blueprint, render_template, session, g

from server.blueprints.user.forms import LoginForm
from server.models import User

index_bp = Blueprint("index", __name__, template_folder="templates")


@index_bp.route("/")
def index():
    login_form = LoginForm()
    user_id = session.get("user_id")
    if user_id:
        g.user = User.get(user_id)

    return render_template("index/index.html", login_form=login_form)
