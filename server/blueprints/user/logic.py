from sqlalchemy.exc import SQLAlchemyError
import requests
from datetime import datetime

from server.models import db, User


def login(email: str, password: str) -> User:
    user = User.get_by_email(email)
    if user and user.check_password(password):
        try:
            # Update the last login time
            user.last_login = db.func.now()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError("Failed to update last login time.") from e
        return user
    raise ValueError("Invalid email or password.")


def register(
        username: str,
        password: str,
        email: str,
        nickname: str,
        date_of_birth=None,
        sex=None,
       
):
    # Check if the username or email already exists
    User.validate_unique(username, email)

    # Create a new user
    try:
        new_user = User(
            username=username,
            nickname=nickname,
            password=User.hash_password(password),  # Hash the password
            email=email,
            date_of_birth=date_of_birth,
            sex=sex,
           
        )
        db.session.add(new_user)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to register user.") from e


def reset_password(user_id: int, new_password: str):
    user = User.get(user_id)
    if not user:
        raise ValueError("User not found.")
    try:
        user.password = User.hash_password(new_password)  # Hash the new password
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to reset password.") from e


def update_user(
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        nickname: str | None = None,
):
    if not any([username, email, nickname]):
        return

    user = User.get(user_id)
    if not user:
        raise ValueError("User not found.")

    if username or email:
        User.validate_unique(username, email, exclude_id=user_id)

    try:
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if nickname is not None:
            user.nickname = nickname
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to update user.") from e


def search_user(username: str) -> list[dict]:
    user = User.search_by_username(username)
    if not user:
        raise ValueError("User not found.")
    return user

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