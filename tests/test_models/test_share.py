import pytest
import uuid
from datetime import datetime, timedelta
from server.models import Share, User
from server.utils.constants import ExerciseType

class TestShareModel:
    def test_create_share(self, session):
        """Test creating a share record"""
        sender = User(username="sender", password="pw", email="sender@ex.com", nickname="Sender")
        receiver = User(username="receiver", password="pw", email="receiver@ex.com", nickname="Receiver")
        session.add_all([sender, receiver])
        session.commit()

        scope = {
            "exercise_types": [ExerciseType.RUNNING.value],
            "body_measurement_types": [],
            "achievements": [],
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        share = Share(
            sender_id=sender.id,
            receiver_id=receiver.id,
            scope=scope,
            start_date=start_date,
            end_date=end_date
        )
        session.add(share)
        session.commit()

        assert share.id is not None
        assert isinstance(share.id, uuid.UUID)
        assert share.sender_id == sender.id
        assert share.receiver_id == receiver.id
        assert share.scope == scope
        assert share.start_date == start_date
        assert share.end_date == end_date
        assert share.created_at is not None
        assert share.deleted is False

    def test_unique_constraint(self, session):
        """Test unique constraint on sender, receiver, and scope"""
        sender = User(username="sender2", password="pw", email="sender2@ex.com", nickname="Sender2")
        receiver = User(username="receiver2", password="pw", email="receiver2@ex.com", nickname="Receiver2")
        session.add_all([sender, receiver])
        session.commit()

        scope = {"exercise_types": ["running"], "body_measurement_types": [], "achievements": [], "start_date": "2024-01-01", "end_date": "2024-01-31"}
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        share1 = Share(
            sender_id=sender.id,
            receiver_id=receiver.id,
            scope=scope,
            start_date=start_date,
            end_date=end_date
        )
        session.add(share1)
        session.commit()

        share2 = Share(
            sender_id=sender.id,
            receiver_id=receiver.id,
            scope=scope,
            start_date=start_date,
            end_date=end_date
        )
        session.add(share2)
        with pytest.raises(Exception):
            session.commit()
        session.rollback()

    def test_scope_validation(self, session):
        """Test that invalid scope raises ValueError"""
        sender = User(username="sender3", password="pw", email="sender3@ex.com", nickname="Sender3")
        receiver = User(username="receiver3", password="pw", email="receiver3@ex.com", nickname="Receiver3")
        session.add_all([sender, receiver])
        session.commit()

        # Invalid scope (not a dict)
        with pytest.raises(ValueError):
            share = Share(
                sender_id=sender.id,
                receiver_id=receiver.id,
                scope="not_a_dict",
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=1)
            )
            session.add(share)
            session.commit()