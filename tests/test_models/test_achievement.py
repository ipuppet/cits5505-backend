import pytest
from server.models import Achievement, User
from server.utils.constants import ExerciseType

class TestAchievementModel:
    def test_create_achievement(self, session):
        """Test creating an achievement"""
        user = User(username="achuser", password="pw", email="ach@ex.com", nickname="Ach")
        session.add(user)
        session.commit()

        achievement = Achievement(
            user_id=user.id,
            exercise_type=ExerciseType.RUNNING,
            milestone=10
        )
        session.add(achievement)
        session.commit()

        assert achievement.id is not None
        assert achievement.user_id == user.id
        assert achievement.exercise_type == ExerciseType.RUNNING
        assert achievement.milestone == 10
        assert achievement.created_at is not None

    def test_get_by_user(self, session):
        """Test get_by_user static method"""
        user = User(username="achuser2", password="pw", email="ach2@ex.com", nickname="Ach2")
        session.add(user)
        session.commit()

        ach1 = Achievement(user_id=user.id, exercise_type=ExerciseType.CYCLING, milestone=20)
        ach2 = Achievement(user_id=user.id, exercise_type=ExerciseType.RUNNING, milestone=5)
        session.add_all([ach1, ach2])
        session.commit()

        achievements = Achievement.get_by_user(user.id).all()
        assert len(achievements) == 2
        assert all(a.user_id == user.id for a in achievements)

    def test_get_by_user_no_user(self):
        """Test get_by_user raises ValueError if user_id is missing"""
        with pytest.raises(ValueError):
            Achievement.get_by_user(None)