import pytest

from server.models import Achievement
from server.utils.constants import ExerciseType


class TestAchievementModel:
    def test_create_achievement(self, db_session, test_user):
        """Test creating an achievement"""
        achievement = Achievement(        user_id=test_user.id, exercise_type=ExerciseType.RUNNING, milestone=10
        )
        db_session.add(achievement)
        db_session.commit()

        assert achievement.id is not None
        assert achievement.user_id == test_user.id
        assert achievement.exercise_type == ExerciseType.RUNNING
        assert achievement.milestone == 10
        assert achievement.created_at is not None
    
    def test_get_by_user(self, db_session, test_user):
        """Test get_by_user static method"""
        ach1 = Achievement(
            user_id=test_user.id, exercise_type=ExerciseType.CYCLING, milestone=20
        )
        ach2 = Achievement(
            user_id=test_user.id, exercise_type=ExerciseType.RUNNING, milestone=5
        )
        db_session.add_all([ach1, ach2])
        db_session.commit()

        achievements = Achievement.get_by_user(test_user.id).all()
        assert len(achievements) == 2
        assert all(a.user_id == test_user.id for a in achievements)
    
    def test_get_by_user_no_user(self):
        """Test get_by_user raises ValueError if user_id is missing"""
        with pytest.raises(ValueError):
            Achievement.get_by_user(None)
