from sqlalchemy.exc import SQLAlchemyError
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


def get_user(user_id: int) -> User:
    user = User.get(user_id)  # Do NOT use as_dict=True
    if not user:
        return None
    return user


def search_user(username: str) -> list[dict]:
    user = User.search_by_username(username)
    if not user:
        raise ValueError("User not found.")
    return user
