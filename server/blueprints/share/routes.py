from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from server.utils.decorators import login_required

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    return render_template("share/index.html")
