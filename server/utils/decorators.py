from functools import wraps
from flask import flash, session, g, jsonify

from server.models import User


def login_required(f):
    """Decorator to check if the user is logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Login required.", "danger")
            raise ValueError("Login required.")
        try:
            user = User.get(session["user_id"])
            g.user = user
        except ValueError:
            session.pop("user_id", None)
            flash("User not found. Please log in again.", "danger")
            raise ValueError("User not found. Please log in again.")
        return f(*args, **kwargs)

    return decorated_function


def api_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = {
                "code": 1,
                "message": "success",
                "data": func(*args, **kwargs)
            }
        except Exception as e:
            response = {
                "code": 0,
                "message": str(e),
                "data": None
            }
        return jsonify(response)

    return wrapper
