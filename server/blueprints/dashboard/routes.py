from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g
from werkzeug.utils import secure_filename
import os

from server.utils.decorators import login_required
from server.models import db, User

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template("dashboard/index.html")

@dashboard_bp.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if file and file.filename:
        filename = secure_filename(file.filename)
        avatar_folder = os.path.join(current_app.static_folder, "avatars")
        os.makedirs(avatar_folder, exist_ok=True)
        file_path = os.path.join(avatar_folder, filename)
        file.save(file_path)
        # Save relative path to DB (e.g. "avatars/filename.png")
        user = g.user
        user.avatar = f"avatars/{filename}"
        db.session.commit()
        flash("Avatar updated!", "success")
    else:
        flash("No file selected.", "danger")
    return redirect(url_for("dashboard.index"))