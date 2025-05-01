from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g
from werkzeug.utils import secure_filename
from datetime import datetime
from server.utils.decorators import login_required
from server.blueprints.user.logic import fetch_weather_forecast


dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

from datetime import timezone

@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    api_key = "5118a8c67aec70333dac3704a6b65bb6"
    weather_forecast = fetch_weather_forecast("Perth", api_key, days=5)

    # Ensure created_at and last_login are UTC-aware
    if g.user.created_at and g.user.created_at.tzinfo is None:
        g.user.created_at = g.user.created_at.replace(tzinfo=timezone.utc)
    if g.user.last_login and g.user.last_login.tzinfo is None:
        g.user.last_login = g.user.last_login.replace(tzinfo=timezone.utc)

    return render_template("dashboard/index.html", weather_forecast=weather_forecast)