import bcrypt
import uuid
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from flask_login import UserMixin

from server.utils.login_manager import login_manager

db = SQLAlchemy()
migrate = Migrate()


class UserConflictError(ValueError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"User with this {field} already exists: {value}")


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
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Exercise.created_at.desc()",
    )
    body_measurements = db.relationship(
        "BodyMeasurement",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="BodyMeasurement.created_at.desc()",
    )
    calorie_intakes = db.relationship(
        "CalorieIntake",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="CalorieIntake.created_at.desc()",
    )
    achievements = db.relationship(
        "Achievement",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Achievement.achieved_at.desc()",
    )
    scheduled_exercises = db.relationship(
        "ScheduledExercise",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ScheduledExercise.scheduled_time.desc()",
    )
    goals = db.relationship(
        "Goal",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="Goal.created_at.desc()",
    )
    shares_sent = db.relationship(
        "Share",
        foreign_keys="Share.sender_id",
        lazy="dynamic",
        backref="sender",
        cascade="all, delete-orphan",
        order_by="Share.created_at.desc()",
    )
    shares_received = db.relationship(
        "Share",
        foreign_keys="Share.receiver_id",
        lazy="dynamic",
        backref="receiver",
        cascade="all, delete-orphan",
        order_by="Share.created_at.desc()",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "date_of_birth": self.date_of_birth,
            "sex": self.sex,
        }

    def exercises_to_list(self) -> list:
        exercises = []
        for exercise in self.exercises.all():
            exercises.append(
                {
                    "type": exercise.type.name,
                    **exercise.metrics,
                    "created_at": exercise.created_at,
                }
            )
        return exercises

    def body_measurements_to_list(self) -> list:
        body_measurements = []
        for measurement in self.body_measurements.all():
            body_measurements.append(
                {
                    "type": measurement.type.name,
                    "value": measurement.value,
                    "created_at": measurement.created_at,
                }
            )
        return body_measurements

    def calorie_intakes_to_list(self) -> list:
        calorie_intakes = []
        for intake in self.calorie_intakes.all():
            calorie_intakes.append(
                {
                    "calories": intake.calories,
                    "description": intake.description,
                    "created_at": intake.created_at,
                }
            )
        return calorie_intakes

    def scheduled_exercises_to_list(self) -> list:
        scheduled_exercises = []
        for exercise in self.scheduled_exercises.all():
            scheduled_exercises.append(
                {
                    "exercise_type": exercise.exercise_type.name,
                    "scheduled_time": exercise.scheduled_time.strftime("%I:%M %p"),
                    "note": exercise.note,
                    "day_of_week": exercise.day_of_week,
                }
            )
        return scheduled_exercises

    @staticmethod
    def get(user_id: int) -> "User":
        if not user_id:
            raise ValueError("ID cannot be empty")
        user = db.session.get(User, int(user_id))
        if not user:
            raise ValueError("User not found")
        return user

    def get_id(self) -> str:
        return self.email

    @staticmethod
    @login_manager.user_loader
    def get_by_email(email: str) -> "User":
        return db.session.query(User).filter_by(email=email).first()

    @staticmethod
    def search_by_username(username: str) -> list[dict]:
        """Fuzzy search for a user by username."""
        if not username:
            raise ValueError("Username cannot be empty")
        users = (
            db.session.query(User).filter(User.username.ilike(f"%{username}%")).all()
        )
        user_list = []
        for user in users:
            user_list.append(user.to_dict())
        return user_list

    @staticmethod
    def hash_password(plain_password: str):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def check_password(self, plain_password: str):
        hashed_password = self.password
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode("utf-8")
        if not isinstance(hashed_password, bytes):
            raise TypeError("Password must be of type bytes")
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)

    @staticmethod
    def validate_unique(
        username: str | None,
        email: str | None,
        exclude_id: int | None = None,
    ):
        """Check if the username or email is unique."""
        if not username and not email:
            raise ValueError("At least one of username or email must be provided")

        query = db.session.query(User)
        if exclude_id:
            query = query.filter(User.id != exclude_id)

        if username:
            if query.filter(User.username == username).first():
                raise UserConflictError("username", username)
        if email:
            if query.filter(User.email == email).first():
                raise UserConflictError("email", email)


class ExerciseType(Enum):
    CYCLING = "cycling"
    RUNNING = "running"
    SWIMMING = "swimming"
    WEIGHTLIFTING = "weight_lifting"
    YOGA = "yoga"

    def __str__(self):
        return self.value.replace("_", " ").title()


METRICS = [
    "distance",
    "duration",
    "weight",
]
METRICS_REQUIREMENTS = {
    ExerciseType.CYCLING: ["distance", "duration"],  # in miters and minutes
    ExerciseType.RUNNING: ["distance", "duration"],
    ExerciseType.SWIMMING: ["distance", "duration"],
    ExerciseType.WEIGHTLIFTING: ["weight", "sets", "reps"],  # in kg
    ExerciseType.YOGA: ["duration"],
}


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.Enum(ExerciseType), nullable=False)
    metrics = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )

    @validates("metrics")
    def validate_metrics(self, key, metrics: dict):
        required_fields = METRICS_REQUIREMENTS.get(self.type, [])
        missing_fields = [f for f in required_fields if f not in metrics]

        if missing_fields:
            error_list = ", ".join([f"Missing '{f}'" for f in missing_fields])
            raise ValueError(
                f"Invalid metrics for {self.type}: {error_list}. "
                f"Required fields: {required_fields}"
            )
        return metrics

    @staticmethod
    def get_by_user(user_id: int, **kwargs):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return (
            db.session.query(Exercise)
            .filter_by(user_id=user_id, **kwargs)
            .order_by(Exercise.created_at.desc())
            .all()
        )


ACHIEVEMENTS = {
    ExerciseType.CYCLING: [100, 1000, 10000],  # in km
    ExerciseType.RUNNING: [50, 500, 5000],  # in km
    ExerciseType.SWIMMING: [10, 100, 1000],  # in km
    ExerciseType.WEIGHTLIFTING: [1000, 10000, 100000],  # in kg
    ExerciseType.YOGA: [10, 100, 1000],  # in minutes
}


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    milestone = db.Column(db.Integer, nullable=False)
    achieved_at = db.Column(
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
            .order_by(Achievement.achieved_at.desc())
            .all()
        )


class BodyMeasurementType(Enum):
    WEIGHT = "weight"
    HEIGHT = "height"
    BODY_FAT = "body_fat"

    def __str__(self):
        return self.value.replace("_", " ").title()


class BodyMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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
            .all()
        )


class CalorieIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    calories = db.Column(db.Float, nullable=False)  # in kcal
    description = db.Column(db.Text, nullable=True)
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
            db.session.query(CalorieIntake)
            .filter_by(user_id=user_id, **kwargs)
            .order_by(CalorieIntake.created_at.desc())
            .all()
        )


class ScheduledExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    note = db.Column(db.Text, nullable=True)
    day_of_week = db.Column(
        db.String(10), nullable=False
    )  # e.g. "Monday", "Tuesday", etc.

    @staticmethod
    def get(schedule_id: int):
        if not schedule_id:
            raise ValueError("ID cannot be empty")
        return db.session.get(ScheduledExercise, int(schedule_id))


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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

    @staticmethod
    def get(goal_id: int):
        if not goal_id:
            raise ValueError("ID cannot be empty")
        return db.session.get(Goal, int(goal_id))


class Share(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    scope = db.Column(db.JSON, nullable=False)
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

    @staticmethod
    def get(share_id: uuid.UUID, include_deleted: bool = False):
        if not share_id:
            raise ValueError("ID cannot be empty")

        query = db.session.query(Share).filter_by(id=share_id)
        if not include_deleted:
            query = query.filter_by(deleted=False)

        return query.one_or_none()

    @staticmethod
    def get_by_sender(sender_id: int):
        if not sender_id:
            raise ValueError("Sender ID cannot be empty")
        return (
            db.session.query(Share).filter_by(sender_id=sender_id, deleted=False).all()
        )

    @staticmethod
    def get_by_receiver(receiver_id: int):
        if not receiver_id:
            raise ValueError("Receiver ID cannot be empty")
        return (
            db.session.query(Share)
            .filter_by(receiver_id=receiver_id, deleted=False)
            .all()
        )
