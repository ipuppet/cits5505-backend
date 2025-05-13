import bcrypt


def hash_password(plain_password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def check_password(plain_password: str, hashed_password: str):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")
    if not isinstance(hashed_password, bytes):
        raise TypeError("Password must be of type bytes")
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
