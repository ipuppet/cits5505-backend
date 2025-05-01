import requests
from datetime import datetime

def fetch_weather_forecast(city, api_key, days=5):
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
        date_str = datetime.utcfromtimestamp(item["dt"]).strftime("%a %d")
        if date_str not in seen_dates and len(weather_forecast) < days:
            weather_forecast.append({
                "date": date_str,
                "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                "temp": round(item["main"]["temp"]),
                "description": item["weather"][0]["main"]
            })
            seen_dates.add(date_str)
    return weather_forecast