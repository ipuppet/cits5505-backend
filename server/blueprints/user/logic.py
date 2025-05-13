import os
import datetime
from werkzeug.datastructures import FileStorage
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.utils import secure_filename
from flask import current_app, url_for
from flask_login import login_user, current_user, logout_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

from server.models import db, User
from server.utils.security import hash_password, check_password
from server.utils.login_manager import login_manager
from server.utils.mail import mail


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
    users = (
        db.session.query(User)
        .filter(
            User.username.ilike(f"%{username}%"),
            User.id != current_user.id,  # Exclude the current user
        )
        .all()
    )
    user_list = []
    for user in users:
        user_list.append(
            {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
            }
        )
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
    user: User | None = None,
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
    if user is None:
        user = current_user

    if not user.is_authenticated:
        raise ValueError("User not found.")

    try:
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if nickname is not None:
            user.nickname = nickname
        if date_of_birth is not None:
            user.date_of_birth = date_of_birth
        if sex is not None:
            user.sex = sex
        if new_password is not None:
            user.password = hash_password(new_password)
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


def reset_password(token: str, new_password: str):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    email = serializer.loads(
        token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=3600
    )
    if not email:
        raise ValueError("Invalid or expired token.")
    user = get_user_by_email(email)
    update_user(new_password=new_password, user=user)


def send_reset_email(email: str) -> str:
    user = get_user_by_email(email)
    if not user:
        raise UserNotFoundError(email)

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = serializer.dumps(email, salt=current_app.config["SECURITY_PASSWORD_SALT"])
    reset_url = url_for("user.reset_password", token=token, _external=True)
    msg = Message(
        subject="Password Reset Request",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[email],
        body=f"To reset your password, click the following link:\n{reset_url}\n\nIf you did not request this, ignore this email.",
    )
    mail.send(msg)

    return token
