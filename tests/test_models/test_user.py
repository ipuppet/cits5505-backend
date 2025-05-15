import pytest
from sqlalchemy.exc import IntegrityError

from server.models import User


class TestUserModel:
    def test_create_user(self, db_session, test_user):
        """Test creating a user with required fields"""
        assert test_user.id is not None
        assert test_user.username == "testuser"
        assert test_user.email == "test@example.com"
        assert test_user.nickname == "Tester"
        assert test_user.created_at is not None

    def test_unique_username(self, db_session, test_user):
        """Test that username must be unique"""
        user2 = User(
            username=test_user.username, password="b", email="b@b.com", nickname="B"
        )
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_unique_email(self, db_session, test_user):
        """Test that email must be unique"""
        user2 = User(
            username="user2", password="b", email=test_user.email, nickname="B"
        )
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_optional_fields(self, db_session, test_user):
        """Test optional fields can be set"""
        test_user.avatar = "avatars/opt.png"
        test_user.sex = "Other"
        db_session.commit()
        assert test_user.avatar == "avatars/opt.png"
        assert test_user.sex == "Other"

    def test_relationships_empty_by_default(self, db_session, test_user):
        """Test relationships are empty for new user"""
        assert test_user.exercises.count() == 0
        assert test_user.body_measurements.count() == 0
        assert test_user.calorie_intakes.count() == 0
        assert test_user.water_intakes.count() == 0
        assert test_user.achievements.count() == 0
        assert test_user.scheduled_exercises.count() == 0
        assert test_user.goals.count() == 0
        assert test_user.shares_sent.count() == 0
        assert test_user.shares_received.count() == 0
