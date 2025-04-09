from functools import wraps
from flask import redirect, url_for, flash, session


def login_required(f):
    """Decorator to check if the user is logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("user.login"))
        return f(*args, **kwargs)

    return decorated_function
