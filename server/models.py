import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from sqlalchemy.schema import UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    nickname = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    last_login = db.Column(
        db.DateTime, nullable=True, default=db.func.current_timestamp()
    )
    tracking_data = db.relationship("TrackingData", backref="user", lazy=True)
    exercises = db.relationship("Exercise", backref="user", lazy=True)
    achievements = db.relationship("Achievement", backref="user", lazy=True)



    @staticmethod
    def get(user_id):
        return db.session.get(User, int(user_id))

    @staticmethod
    def hash_password(plain_password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def check_password(self, plain_password):
        if isinstance(self.password, str):
            hashed_password = self.password.encode("utf-8")
        elif isinstance(self.password, bytes):
            hashed_password = self.password
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
    
class TrackingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    steps = db.Column(db.Integer, nullable=True)
    calories = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    
class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)  # e.g., Jogging
    category = db.Column(db.String(50))               # e.g., Cardio
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)  # "I ran 5km today!"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    share_uuid = db.Column(db.String(100), nullable=True)
    __table_args__ = (
        UniqueConstraint('share_uuid', name='uq_achievement_share_uuid'),
    )
