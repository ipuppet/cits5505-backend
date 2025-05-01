from flask import Blueprint, render_template, g
from server.utils.decorators import login_required
from server.blueprints.dashboard.logic import fetch_weather_forecast

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    weather_forecast = fetch_weather_forecast("Perth", days=5)
    return render_template("dashboard/index.html", weather_forecast=weather_forecast)
