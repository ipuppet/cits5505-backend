import uuid
from datetime import datetime, timedelta

import pytest

from server.models import Share
from server.utils.constants import ExerciseType


class TestShareModel:
    def test_create_share(self, db_session, test_user, test_receiver):
        """Test creating a share record"""
        sender = test_user
        receiver = test_receiver

        scope = {
            "exercise_types": [ExerciseType.RUNNING.value],
            "body_measurement_types": [],
            "achievements": [],
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        share = Share(
            sender_id=sender.id,
            receiver_id=receiver.id,
            scope=scope,
            start_date=start_date,
            end_date=end_date,
        )
        db_session.add(share)
        db_session.commit()

        assert share.id is not None
        assert isinstance(share.id, uuid.UUID)
        assert share.sender_id == sender.id
        assert share.receiver_id == receiver.id
        assert share.scope == scope
        assert share.start_date == start_date
        assert share.end_date == end_date
        assert share.created_at is not None
        assert share.deleted is False

    def test_unique_constraint(self, db_session, test_user, test_receiver):
        """Test unique constraint on sender, receiver, and scope"""
        sender = test_user
        receiver = test_receiver

        scope = {
            "exercise_types": ["running"],
            "body_measurement_types": [],
            "achievements": [],
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        share1 = Share(
            sender_id=sender.id,
            receiver_id=receiver.id,
            scope=scope,
            start_date=start_date,
            end_date=end_date,
        )
        db_session.add(share1)
        db_session.commit()

        share2 = Share(
            sender_id=sender.id,
            receiver_id=receiver.id,
            scope=scope,
            start_date=start_date,
            end_date=end_date,
        )
        db_session.add(share2)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

    def test_scope_validation(self, db_session, test_user, test_receiver):
        """Test that invalid scope raises ValueError"""
        sender = test_user
        receiver = test_receiver

        # Invalid scope (not a dict)
        with pytest.raises(ValueError):
            share = Share(
                sender_id=sender.id,
                receiver_id=receiver.id,
                scope="not_a_dict",
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=1),
            )
            db_session.add(share)
            db_session.commit()
