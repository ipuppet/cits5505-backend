import bcrypt
import uuid
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import validates

db = SQLAlchemy()
migrate = Migrate()


class UserConflictError(ValueError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"User with this {field} already exists: {value}")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    nickname = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.String(256), nullable=True)  # Stores the relative path to the avatar image
    date_of_birth = db.Column(db.Date, nullable=True)
    sex = db.Column(db.String(10), nullable=True)  # e.g. 'Male', 'Female', 'Other'

    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    last_login = db.Column(
        db.DateTime, nullable=True, default=db.func.current_timestamp()
    )

    exercises = db.relationship(
        "Exercise", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    body_measurements = db.relationship("BodyMeasurement", backref="user", lazy=True)
    shares_sent = db.relationship(
        "Share", foreign_keys="Share.sender_id", backref="sender", lazy=True
    )
    shares_received = db.relationship(
        "Share", foreign_keys="Share.receiver_id", backref="receiver", lazy=True
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
        for exercise in self.exercises:
            exercises.append({
                'type': exercise.type.name,
                **exercise.metrics,
                'created_at': exercise.created_at,
            })
        return exercises

    def body_measurements_to_list(self) -> list:
        body_measurements = []
        for measurement in self.body_measurements:
            body_measurements.append({
                'type': measurement.type.name,
                'value': measurement.value,
                'unit': measurement.unit,
                'created_at': measurement.created_at,
            })
        return body_measurements

    @staticmethod
    def get(user_id: int) -> "User":
        if not user_id:
            raise ValueError("ID cannot be empty")
        user = db.session.get(User, int(user_id))
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def get_by_email(email: str) -> "User":
        if not email:
            raise ValueError("Email cannot be empty")
        return db.session.query(User).filter_by(email=email).first()

    @staticmethod
    def search_by_username(username: str) -> list[dict]:
        """Fuzzy search for a user by username."""
        if not username:
            raise ValueError("Username cannot be empty")
        users = db.session.query(User).filter(User.username.ilike(f"%{username}%")).all()
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


METRICS_REQUIREMENTS = {
    ExerciseType.CYCLING: ["distance_km", "duration_min"],
    ExerciseType.RUNNING: ["distance_km", "duration_min"],
    ExerciseType.SWIMMING: ["distance_m", "duration_min"],
    ExerciseType.WEIGHTLIFTING: ["weight_kg", "sets", "reps"],
    ExerciseType.YOGA: ["duration_min"],
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
    def get(exercise_id: int):
        if not exercise_id:
            raise ValueError("ID cannot be empty")
        return db.session.get(Exercise, int(exercise_id))

    @staticmethod
    def get_by_user(user_id: int):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return db.session.query(Exercise).filter_by(user_id=user_id).all()


class BodyMeasurementType(Enum):
    WEIGHT = "weight"
    HEIGHT = "height"
    BODY_FAT = "body_fat"

    def __str__(self):
        return self.value.replace("_", " ").title()


BODY_MEASUREMENT_UNITS = {
    BodyMeasurementType.WEIGHT: ["kg", "lbs"],
    BodyMeasurementType.HEIGHT: ["cm", "inches"],
    BodyMeasurementType.BODY_FAT: ["%"],
}

class ScheduledExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    note = db.Column(db.Text, nullable=True)
    day_of_week = db.Column(db.String(10), nullable=False)  # e.g. "Monday", "Tuesday", etc.

    user = db.relationship("User", backref="scheduled_exercises")
    
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    exercise_type = db.Column(db.Enum(ExerciseType), nullable=False)

    target_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String(32), nullable=True)  # e.g. "kg", "km", "min"
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship("User", backref="goals")
    
class BodyMeasurement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.Enum(BodyMeasurementType), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        index=True,
    )

    @validates("unit")
    def validate_unit(self, key, unit: str):
        if unit not in BODY_MEASUREMENT_UNITS.get(self.type, []):
            raise ValueError(
                f"Invalid unit '{unit}' for {self.type}. "
                f"Allowed units: {BODY_MEASUREMENT_UNITS[self.type]}"
            )
        return unit

    @staticmethod
    def get(body_measurement_id: int):
        if not body_measurement_id:
            raise ValueError("ID cannot be empty")
        return db.session.get(BodyMeasurement, int(body_measurement_id))

    @staticmethod
    def get_by_user(user_id: int):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return db.session.query(BodyMeasurement).filter_by(user_id=user_id).all()


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
