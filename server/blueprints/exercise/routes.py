from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from server.utils.decorators import login_required

exercise_bp = Blueprint("exercise", __name__, template_folder="templates")


@exercise_bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("exercise/index.html")
