from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from server.utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("dashboard/index.html")
