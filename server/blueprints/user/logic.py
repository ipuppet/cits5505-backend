from server.models import db, User


def login(email: str, password: str) -> User:
    user = User.query.filter_by(email=email).first()
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
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
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


def get_user(user_id: int) -> User:
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found.")
    return user
