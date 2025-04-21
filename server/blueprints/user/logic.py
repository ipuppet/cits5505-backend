from server.models import db, User


def login(email: str, password: str) -> User:
    user = User.get_by_email(email)
    if user and user.check_password(password):
        return user
    raise ValueError("Invalid email or password.")


def register(
    username: str,
    password: str,
    email: str,
    nickname: str = None,
) -> bool:
    # Check if the username or email already exists
    if User.unique_user(username, email):
        raise ValueError("Username or email already exists.")

    # Create a new user
    try:
        new_user = User(
            username=username,
            nickname=nickname or username,
            password=User.hash_password(password),  # Hash the password
            email=email,
        )
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return True


def reset_password(user_id: int, new_password: str) -> bool:
    user = User.get(user_id)
    if not user:
        raise ValueError("User not found.")
    try:
        user.password = User.hash_password(new_password)  # Hash the new password
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return True


def update_user(
    user_id: int,
    username: str = None,
    email: str = None,
    nickname: str = None,
) -> bool:
    user = User.get(user_id)
    if not user:
        raise ValueError("User not found.")
    if User.unique_user(username, email):
        raise ValueError("Username or email already exists.")
    try:
        if username:
            user.username = username
        if email:
            user.email = email
        if nickname:
            user.nickname = nickname
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    return True


def get_user(user_id: int) -> User:
    user = User.get(user_id, as_dict=True)
    if not user:
        raise ValueError("User not found.")
    return user
