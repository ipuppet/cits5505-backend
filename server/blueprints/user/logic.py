import os
import datetime
from werkzeug.datastructures import FileStorage
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.utils import secure_filename
from flask import current_app
from flask_login import login_user, current_user, logout_user

from server.models import db, User
from server.utils.security import hash_password, check_password
from server.utils.login_manager import login_manager


class UserConflictError(Exception):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"User with {field} '{value}' already exists.")


class UserNotFoundError(Exception):
    def __init__(self, identifier):
        super().__init__(f"User with identifier '{identifier}' not found.")


@login_manager.user_loader
def get_user_by_id(user_id: int) -> User | None:
    """Finds a user by their ID."""
    if not user_id:
        return None
    user = db.session.get(User, int(user_id))
    return user


def get_user_by_email(email: str) -> User | None:
    """Finds a user by their email."""
    if not email:
        return None
    user = db.session.query(User).filter_by(email=email).first()
    return user


def search_user(username: str) -> list[dict]:
    """Fuzzy search for a user by username."""
    if not username:
        raise ValueError("Username cannot be empty")
    users = db.session.query(User).filter(User.username.ilike(f"%{username}%")).all()
    user_list = []
    for user in users:
        user_list.append(user.to_dict())
    if not user_list:
        raise UserNotFoundError(username)
    return user_list


def check_user_integrity(e, username, email):
    if "unique" in str(e).lower():
        if "username" in str(e.orig):
            raise UserConflictError("username", username)
        elif "email" in str(e.orig):
            raise UserConflictError("email", email)
    raise RuntimeError("Failed to create user.") from e


def login(email: str, plain_password: str, remember_me: bool) -> User:
    user = get_user_by_email(email)
    if user and check_password(plain_password, user.password):
        try:
            # Update the last login time
            user.last_login = datetime.datetime.now(datetime.UTC)
            db.session.commit()
            login_user(user, remember=remember_me)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError("Failed to update last login time.") from e
        return user
    raise ValueError("Invalid email or password.")


def logout():
    logout_user()


def create_user(
    username: str,
    password: str,
    email: str,
    nickname: str,
    date_of_birth: datetime.date | None = None,
    sex: str | None = None,
):
    try:
        new_user = User(
            username=username,
            nickname=nickname,
            password=hash_password(password),  # Hash the password
            email=email,
            date_of_birth=date_of_birth,
            sex=sex,
        )
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        check_user_integrity(e, username, email)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to register user.") from e


def update_user(
    username: str | None = None,
    email: str | None = None,
    nickname: str | None = None,
    date_of_birth: datetime.date | None = None,
    sex: str | None = None,
    new_password: str | None = None,
):
    if not any(
        [
            username,
            email,
            nickname,
            date_of_birth,
            sex,
            new_password,
        ]
    ):
        return

    if not current_user.is_authenticated:
        raise ValueError("User not found.")

    try:
        if username is not None:
            current_user.username = username
        if email is not None:
            current_user.email = email
        if nickname is not None:
            current_user.nickname = nickname
        if date_of_birth is not None:
            current_user.date_of_birth = date_of_birth
        if sex is not None:
            current_user.sex = sex
        if new_password is not None:
            current_user.password = hash_password(new_password)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        check_user_integrity(e, username, email)
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError("Failed to update user.") from e


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
