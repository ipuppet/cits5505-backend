from flask import Blueprint, render_template, g
from server.utils.decorators import login_required
from server.blueprints.dashboard.logic import fetch_weather_forecast

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")


<<<<<<< HEAD
@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
=======
@dashboard_bp.route("/", methods=["GET"])
>>>>>>> 78f5ef41f81d91b12f819b002c260a5e5ce20d2b
@login_required
def index():
    weather_forecast = fetch_weather_forecast("Perth", days=5)
    return render_template("dashboard/index.html", weather_forecast=weather_forecast)
