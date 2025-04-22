from flask import Blueprint, render_template, session
from server.blueprints.user.logic import get_user

index_bp = Blueprint("index", __name__, template_folder="templates")


@index_bp.route("/")
def index():
    user = None
    if "user_id" in session:
        try:
            user = get_user(session["user_id"])
        except Exception:
            user = None
    return render_template("index/index.html", user=user)
