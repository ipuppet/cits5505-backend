from functools import wraps
from flask import redirect, url_for, flash, session, g

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
