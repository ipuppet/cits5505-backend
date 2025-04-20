import bcrypt
import uuid
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates


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

    @staticmethod
    def get(user_id):
        if not user_id:
            raise ValueError("ID cannot be empty")
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


class ExerciseType(Enum):
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WEIGHTLIFTING = "weightlifting"
    YOGA = "yoga"

    def __str__(self):
        return self.value


METRICS_REQUIREMENTS = {
    ExerciseType.RUNNING: ["distance_km", "duration"],
    ExerciseType.CYCLING: ["distance_km", "duration"],
    ExerciseType.SWIMMING: ["distance_m", "duration"],
    ExerciseType.WEIGHTLIFTING: ["weight_kg", "sets", "reps"],
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
    def validate_metrics(self, key, metrics):
        if not isinstance(metrics, dict):
            raise ValueError("Metrics must be a dictionary")

        required_fields = METRICS_REQUIREMENTS.get(self.type, [])
        errors = []
        for field in required_fields:
            if field not in metrics:
                errors.append(f"Missing '{field}'")
                break
        if errors:
            raise ValueError(
                f"Invalid metrics for {self.type.name}: {', '.join(errors)}. "
                f"Required fields: {required_fields}"
            )
        return metrics

    @staticmethod
    def get(exercise_id):
        if not exercise_id:
            raise ValueError("ID cannot be empty")
        return db.session.get(Exercise, int(exercise_id))


class BodyMeasurementType(Enum):
    WEIGHT = "weight"
    HEIGHT = "height"
    BODY_FAT = "body_fat"

    def __str__(self):
        return self.value


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

    @staticmethod
    def get(body_measurement_id):
        if not body_measurement_id:
            raise ValueError("ID cannot be empty")
        return db.session.get(BodyMeasurement, int(body_measurement_id))


class Share(db.Model):
    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    scope = db.Column(db.Text, nullable=False)
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
    def get(share_id, include_deleted=False):
        if not share_id:
            raise ValueError("ID cannot be empty")
        try:
            share_id = uuid.UUID(share_id) if isinstance(share_id, str) else share_id
        except (ValueError, AttributeError):
            raise ValueError("Invalid share ID format")

        query = Share.query.filter_by(id=share_id)
        if not include_deleted:
            query = query.filter_by(deleted=False)

        return query.one_or_none()
