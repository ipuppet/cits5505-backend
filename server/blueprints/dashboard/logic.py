import requests
from datetime import datetime, timezone
from flask_login import current_user

from server.models import ACHIEVEMENTS


def fetch_weather_forecast(city, days=5):
    api_key = "5118a8c67aec70333dac3704a6b65bb6"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "units": "metric",
        "appid": api_key
    }
    resp = requests.get(url, params=params, timeout=5)
    data = resp.json()

    weather_forecast = []
    seen_dates = set()
    for item in data.get("list", []):
        date_str = datetime.fromtimestamp(item["dt"], tz=timezone.utc).strftime("%a %d")
        if date_str not in seen_dates and len(weather_forecast) < days:
            weather_forecast.append({
                "date": date_str,
                "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                "temp": round(item["main"]["temp"]),
                "description": item["weather"][0]["main"]
            })
            seen_dates.add(date_str)
    return weather_forecast


def get_all_achievements() -> dict:
    return ACHIEVEMENTS


def get_achievements_dict() -> dict:
    achievements = {}
    for achievement in current_user.achievements:
        if achievement.exercise_type not in achievements:
            achievements[achievement.exercise_type] = []
        achievements[achievement.exercise_type].append(achievement.milestone)
    return achievements
