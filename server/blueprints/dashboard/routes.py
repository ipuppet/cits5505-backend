from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g
from werkzeug.utils import secure_filename
import os
import requests
from datetime import datetime
from server.utils.decorators import login_required
from server.models import db, User

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    api_key = "5118a8c67aec70333dac3704a6b65bb6"
    weather_forecast = []
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": "Perth",
            "units": "metric",
            "appid": api_key
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        seen_dates = set()
        for item in data.get("list", []):
            date_str = datetime.utcfromtimestamp(item["dt"]).strftime("%a %d")
            if date_str not in seen_dates and len(weather_forecast) < 5:
                weather_forecast.append({
                    "date": date_str,
                    "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                    "temp": round(item["main"]["temp"]),
                    "description": item["weather"][0]["main"]
                })
                seen_dates.add(date_str)
    except Exception as e:
        print("Weather error:", e)
        weather_forecast = []

    return render_template("dashboard/index.html", weather_forecast=weather_forecast)

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