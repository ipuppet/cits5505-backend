import uuid
from sqlalchemy.exc import SQLAlchemyError
from server.models import db, Share


def get_shared(share_id: uuid.UUID) -> Share:
    """
    Retrieve a share record by its ID.

    Args:
        share_id (uuid.UUID): The ID of the share to retrieve.

    Returns:
        Share: The retrieved Share object, or None if not found.
    """
    try:
        share = Share.get(share_id)
        if not share:
            raise ValueError("Share not found")
        return share
    except SQLAlchemyError as e:
        raise ValueError(f"Error retrieving share: {str(e)}")


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
        raise ValueError(f"Error creating share: {str(e)}")


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
        raise ValueError(f"Error deleting share: {str(e)}")
