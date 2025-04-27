from functools import wraps
from flask import redirect, url_for, flash, session, g, jsonify

from server.blueprints.user.logic import get_user


def login_required(f):
    """Decorator to check if the user is logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('index.index'))
        try:
            user = get_user(session["user_id"])
            g.user = user
        except ValueError:
            flash("User not found. Please log in again.", "danger")
            session.pop("user_id", None)
            return redirect(url_for('index.index'))
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
