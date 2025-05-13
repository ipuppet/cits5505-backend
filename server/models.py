import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from flask_login import UserMixin

from server.utils.validators import validate_metrics, validate_scope
from server.utils.constants import ExerciseType, BodyMeasurementType

db = SQLAlchemy()
migrate = Migrate()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    nickname = db.Column(db.Text, nullable=False)
    avatar = db.Column(
        db.String(256), nullable=True
    )  # Stores the relative path to the avatar image
    date_of_birth = db.Column(db.Date, nullable=True)
    sex = db.Column(db.String(10), nullable=True)  # e.g. 'Male', 'Female', 'Other'

    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    last_login = db.Column(
        db.DateTime, nullable=True, default=db.func.current_timestamp()
    )

    exercises = db.relationship(
        "Exercise",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Exercise.created_at.desc()",
    )
    body_measurements = db.relationship(
        "BodyMeasurement",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="BodyMeasurement.created_at.desc()",
    )
    calorie_intakes = db.relationship(
        "CalorieIntake",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="CalorieIntake.created_at.desc()",
    )
    water_intakes = db.relationship(
        "WaterIntake",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="WaterIntake.created_at.desc()",
    )
    achievements = db.relationship(
        "Achievement",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Achievement.created_at.desc()",
    )
    scheduled_exercises = db.relationship(
        "ScheduledExercise",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ScheduledExercise.scheduled_time.desc()",
    )
    goals = db.relationship(
        "Goal",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Goal.created_at.desc()",
    )
    shares_sent = db.relationship(
        "Share",
        backref="sender",  # Create `.sender` attribute on Share
        foreign_keys="Share.sender_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Share.created_at.desc()",
        primaryjoin="and_(Share.sender_id==User.id, Share.deleted==False)",
    )
    shares_received = db.relationship(
        "Share",
        backref="receiver",  # Create `.receiver` attribute on Share
        foreign_keys="Share.receiver_id",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Share.created_at.desc()",
        primaryjoin="and_(Share.receiver_id==User.id, Share.deleted==False)",
    )


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    type = db.Column(db.Enum(ExerciseType), nullable=False)
    metrics = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )

    @validates("metrics")
    def validate_metrics(self, _key, metrics: dict):
        return validate_metrics(self.type, metrics)

    @staticmethod
    def get_by_user(user_id: int, **kwargs):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return (
            db.session.query(Exercise)
            .filter_by(user_id=user_id, **kwargs)
            .order_by(Exercise.created_at.desc())
        )


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    milestone = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
    )

    @staticmethod
    def get_by_user(user_id: int, **kwargs):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return (
            db.session.query(Achievement)
            .filter_by(user_id=user_id, **kwargs)
            .order_by(Achievement.created_at.desc())
        )


class BodyMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    type = db.Column(db.Enum(BodyMeasurementType), nullable=False)
    value = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )

    @staticmethod
    def get_by_user(user_id: int, **kwargs):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return (
            db.session.query(BodyMeasurement)
            .filter_by(user_id=user_id, **kwargs)
            .order_by(BodyMeasurement.created_at.desc())
        )


class CalorieIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    calories = db.Column(db.Float, nullable=False)  # in kcal
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )


class WaterIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    amount = db.Column(db.Float, nullable=False)  # in liters
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )


class ScheduledExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    note = db.Column(db.Text, nullable=True)
    day_of_week = db.Column(db.String(10), nullable=False)  # "Monday", "Tuesday" etc.


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    description = db.Column(db.String(256), nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    metric = db.Column(db.String(64), nullable=False)
    target_value = db.Column(db.Float, nullable=False)
    achieved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    @hybrid_property
    def current_value(self):
        if self.achieved:
            return self.target_value
        # Calculate the current value based on the user's exercises
        exercises = (
            db.session.query(Exercise)
            .filter_by(user_id=self.user_id, type=self.exercise_type)
            .all()
        )
        total = 0.0
        for ex in exercises:
            value = float(ex.metrics.get(self.metric, 0))
            total += value
        if total >= self.target_value:
            self.achieved = True
        return total


class Share(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    sender_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    scope = db.Column(db.JSON, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    __table_args__ = (
        db.UniqueConstraint(
            "sender_id", "receiver_id", "scope", name="uq_share_relationship"
        ),
    )

    @validates("scope")
    def validate_scope(self, _key, scope: dict):
        return validate_scope(scope)
