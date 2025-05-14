import uuid

from sqlalchemy.exc import SQLAlchemyError

from server.models import db, Share, Exercise, BodyMeasurement, Achievement
from server.utils.constants import ExerciseType, BodyMeasurementType


def get_shared_data(
    sender_id: int,
    scope: dict,
    start_date,
    end_date,
) -> dict[str, list]:
    shared = {
        "exercises": [],
        "body_measurements": [],
        "achievements": [],
    }
    try:
        exercise_types = scope.get("exercise_types", [])
        for exercise_type in exercise_types:
            exercise = (
                Exercise.get_by_user(
                    sender_id,
                    type=ExerciseType[exercise_type],
                )
                .filter(
                    Exercise.created_at >= start_date,
                    Exercise.created_at <= end_date,
                )
                .all()
            )
            if exercise:
                shared["exercises"] += exercise
        body_measurement_types = scope.get("body_measurement_types", [])
        for body_measurement_type in body_measurement_types:
            body_measurement = (
                BodyMeasurement.get_by_user(
                    sender_id,
                    type=BodyMeasurementType[body_measurement_type],
                )
                .filter(
                    BodyMeasurement.created_at >= start_date,
                    BodyMeasurement.created_at <= end_date,
                )
                .all()
            )
            if body_measurement:
                shared["body_measurements"] += body_measurement
        achievements = scope.get("achievements", [])
        for achievement in achievements:
            achievement = (
                Achievement.get_by_user(
                    sender_id,
                    type=ExerciseType[achievement],
                )
                .filter(
                    Achievement.created_at >= start_date,
                    Achievement.created_at <= end_date,
                )
                .all()
            )
            if achievement:
                shared["achievements"] += achievement
        return shared
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error retrieving shared data: {str(e)}")


def get_shared(share_id: uuid.UUID) -> dict[str, list]:
    """
    Retrieve a share record by its ID.

    Args:
        share_id (uuid.UUID): The ID of the share to retrieve.

    Returns:
        Share: The dictionary containing the shared data.
    """
    try:
        share = db.session.query(Share).filter_by(id=share_id, deleted=False).first()
        if not share:
            raise ValueError("Share not found")
        return get_shared_data(
            share.sender_id, share.scope, share.start_date, share.end_date
        )
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error retrieving share: {str(e)}")


def create_share(
    sender_id: int,
    receiver_id: int,
    scope: dict,
    start_date,
    end_date,
) -> Share:
    """
    Create a new share record in the database.

    Args:
        sender_id (int): The ID of the user sending the share.
        receiver_id (int): The ID of the user receiving the share.
        scope (dict): The scope of the share.

    Returns:
        Share: The created Share object.
    """
    try:
        share = Share(
            sender_id=sender_id,
            receiver_id=receiver_id,
            scope=scope,
            start_date=start_date,
            end_date=end_date,
        )
        db.session.add(share)
        db.session.commit()
        return share
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error creating share: {str(e)}")


def delete_share(share_id: uuid.UUID):
    """
    Delete a share record from the database.

    Args:
        share_id (uuid.UUID): The ID of the share to delete.
    """
    try:
        share = db.session.query(Share).filter_by(id=share_id, deleted=False).first()
        if not share:
            raise ValueError("Share not found")

        share.deleted = True
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error deleting share: {str(e)}")
