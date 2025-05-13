from functools import wraps
from flask import jsonify


def api_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = {
                "code": 1,
                "message": "success",
                "data": func(*args, **kwargs),
            }
        except Exception as e:
            response = {
                "code": 0,
                "message": str(e),
                "data": None,
            }
        return jsonify(response)

    return wrapper
