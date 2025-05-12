import uuid
from sqlalchemy.exc import SQLAlchemyError

from server.models import db, Share, Exercise, BodyMeasurement, Achievement


def get_shared(share_id: uuid.UUID) -> dict[str, list]:
    """
    Retrieve a share record by its ID.

    Args:
        share_id (uuid.UUID): The ID of the share to retrieve.

    Returns:
        Share: The dictionary containing the shared data.
    """
    try:
        share = Share.get(share_id)
        if not share or share.deleted:
            raise ValueError("Share not found")
        shared = {
            "exercises": [],
            "body_measurements": [],
            "achievements": [],
        }
        exercise_types = share.scope.get("exercise_types", [])
        for exercise_type in exercise_types:
            exercise = (
                Exercise.get_by_user(
                    share.sender_id,
                    type=exercise_type,
                )
                .filter(
                    Exercise.date >= share.scope.get("start_date"),
                    Exercise.date <= share.scope.get("end_date"),
                )
                .all()
            )
            if exercise:
                shared["exercises"].append(exercise)
        body_measurement_types = share.scope.get("body_measurement_types", [])
        for body_measurement_type in body_measurement_types:
            body_measurement = (
                BodyMeasurement.get_by_user(
                    share.sender_id,
                    type=body_measurement_type,
                )
                .filter(
                    BodyMeasurement.date >= share.scope.get("start_date"),
                    BodyMeasurement.date <= share.scope.get("end_date"),
                )
                .all()
            )
            if body_measurement:
                shared["body_measurements"].append(body_measurement)
        achievements = share.scope.get("achievements", [])
        for achievement in achievements:
            achievement = (
                Achievement.get_by_user(
                    share.sender_id,
                    type=achievement,
                )
                .filter(
                    Achievement.date >= share.scope.get("start_date"),
                    Achievement.date <= share.scope.get("end_date"),
                )
                .all()
            )
            if achievement:
                shared["achievements"].append(achievement)
        return shared
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error retrieving share: {str(e)}")


def create_share(
    sender_id: int,
    receiver_id: int,
    scope: dict,
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
        share = Share.get(share_id)
        if not share:
            raise ValueError("Share not found")

        share.deleted = True
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error deleting share: {str(e)}")
