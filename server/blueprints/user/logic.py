import os
from werkzeug.datastructures import FileStorage
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from flask import current_app
from flask_login import login_user, current_user, logout_user

from server.models import db, User


def login(email: str, password: str, remember_me: bool) -> User:
    user = User.get_by_email(email)
    if user and user.check_password(password):
        try:
            # Update the last login time
            user.last_login = db.func.now()
            db.session.commit()
            login_user(user, remember=remember_me)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError("Failed to update last login time.") from e
        return user
    raise ValueError("Invalid email or password.")


def logout():
    logout_user()


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


def reset_password(new_password: str):
    if not current_user.is_authenticated:
        raise ValueError("User not found.")
    try:
        current_user.password = User.hash_password(
            new_password
        )  # Hash the new password
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to reset password.") from e


def update_user(
    username: str | None = None,
    email: str | None = None,
    nickname: str | None = None,
):
    if not any([username, email, nickname]):
        return

    if not current_user.is_authenticated:
        raise ValueError("User not found.")

    if username or email:
        User.validate_unique(username, email, exclude_id=current_user.id)

    try:
        if username is not None:
            current_user.username = username
        if email is not None:
            current_user.email = email
        if nickname is not None:
            current_user.nickname = nickname
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to update user.") from e


def search_user(username: str) -> list[dict]:
    user = User.search_by_username(username)
    if not user:
        raise ValueError("User not found.")
    return user


def update_avatar(file: FileStorage):
    filename = secure_filename(file.filename)
    avatar_folder = os.path.join(current_app.static_folder, "avatars")
    os.makedirs(avatar_folder, exist_ok=True)
    file_path = os.path.join(avatar_folder, filename)

    old_avatar_path = (
        os.path.join(avatar_folder, current_user.avatar.split("/")[-1])
        if current_user.avatar
        else None
    )
    try:
        if old_avatar_path and os.path.exists(old_avatar_path):
            os.remove(old_avatar_path)
    except OSError as e:
        raise RuntimeError(f"Failed to delete old avatar: {e}") from e

    try:
        file.save(file_path)
        current_user.avatar = f"avatars/{filename}"
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise RuntimeError("Failed to upload avatar.") from e
    except Exception as e:
        # Handle any other exceptions that may occur
        if os.path.exists(file_path):
            os.remove(file_path)
        raise RuntimeError(f"Failed to save avatar: {e}") from e
