from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from server.utils.decorators import login_required

browse_bp = Blueprint("browse", __name__, template_folder="templates")


@browse_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("browse/index.html")
