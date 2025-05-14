import pytest
from server.models import User

class TestUserModel:
    def test_create_user(self, session):
        """Test creating a user with required fields"""
        user = User(
            username="testuser",
            password="testpass",
            email="test@example.com",
            nickname="Tester"
        )
        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.nickname == "Tester"
        assert user.created_at is not None

    def test_unique_username(self, session):
        """Test that username must be unique"""
        user1 = User(username="uniqueuser", password="a", email="a@a.com", nickname="A")
        user2 = User(username="uniqueuser", password="b", email="b@b.com", nickname="B")
        session.add(user1)
        session.commit()
        session.add(user2)
        with pytest.raises(Exception):
            session.commit()
        session.rollback()

    def test_unique_email(self, session):
        """Test that email must be unique"""
        user1 = User(username="user1", password="a", email="same@email.com", nickname="A")
        user2 = User(username="user2", password="b", email="same@email.com", nickname="B")
        session.add(user1)
        session.commit()
        session.add(user2)
        with pytest.raises(Exception):
            session.commit()
        session.rollback()

    def test_optional_fields(self, session):
        """Test optional fields can be set"""
        user = User(
            username="optuser",
            password="pw",
            email="opt@example.com",
            nickname="Opt",
            avatar="avatars/opt.png",
            date_of_birth=None,
            sex="Other"
        )
        session.add(user)
        session.commit()
        assert user.avatar == "avatars/opt.png"
        assert user.sex == "Other"

    def test_relationships_empty_by_default(self, session):
        """Test relationships are empty for new user"""
        user = User(username="reluser", password="pw", email="rel@rel.com", nickname="Rel")
        session.add(user)
        session.commit()
        assert user.exercises.count() == 0
        assert user.body_measurements.count() == 0
        assert user.calorie_intakes.count() == 0
        assert user.water_intakes.count() == 0
        assert user.achievements.count() == 0
        assert user.scheduled_exercises.count() == 0
        assert user.goals.count() == 0
        assert user.shares_sent.count() == 0
        assert user.shares_received.count() == 0