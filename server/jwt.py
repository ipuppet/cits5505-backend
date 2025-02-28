import bcrypt
from flask import current_app
from flask_jwt_extended import JWTManager

from .db import db

jwt = JWTManager(current_app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    def hash_password(plain_password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed_password

    def check_password(self, plain_password):
        hashed_password = self.password.encode("utf-8")
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)


@jwt.user_identity_loader
def user_identity_lookup(user: User):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()
