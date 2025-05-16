import pytest
from server.models import Exercise
from server.utils.constants import ExerciseType


class TestExerciseModel:

    @pytest.mark.parametrize(
        "exercise_type,valid_metrics",
        [
            (ExerciseType.RUNNING, {"distance": 5.0, "duration": 30}),
            (ExerciseType.WEIGHTLIFTING, {"weight": 50.0, "sets": 3, "reps": 12}),
            (ExerciseType.YOGA, {"duration": 45}),
        ],
    )
    def test_valid_exercise_creation(self, db_session, exercise_type, valid_metrics):
        """Test valid exercise creation with correct metrics"""
        exercise = Exercise(user_id=1, type=exercise_type, metrics=valid_metrics)
        db_session.add(exercise)
        db_session.commit()

        assert exercise.id is not None
        assert exercise.created_at is not None
        assert exercise.metrics == valid_metrics

    @pytest.mark.parametrize(
        "exercise_type,invalid_metrics",
        [
            # Single field missing
            (ExerciseType.RUNNING, {"duration": 30}),
            (ExerciseType.CYCLING, {"distance": 10}),
            (ExerciseType.SWIMMING, {"distance": 50}),
            (ExerciseType.WEIGHTLIFTING, {"weight": 50, "sets": 3}),
            # Multiple fields missing
            (ExerciseType.RUNNING, {}),
            (ExerciseType.WEIGHTLIFTING, {"reps": 12}),
            # Invalid type
            (ExerciseType.YOGA, "invalid_string"),
        ],
        ids=[
            "running_missing_distance",
            "cycling_missing_duration",
            "swimming_missing_duration",
            "weightlifting_missing_reps",
            "running_all_missing",
            "weightlifting_multiple_missing",
            "yoga_invalid_type",
        ],
    )
    def test_invalid_metrics_validation(self, exercise_type, invalid_metrics):
        """Test validation of required metrics fields"""
        with pytest.raises(ValueError):
            Exercise(user_id=1, type=exercise_type, metrics=invalid_metrics)

    def test_get_by_user(self, db_session, test_user):
        """Test get_by_user static method"""
        exercise1 = Exercise(
            user_id=test_user.id,
            type=ExerciseType.RUNNING,
            metrics={"distance": 5.0, "duration": 30},
        )
        exercise2 = Exercise(
            user_id=test_user.id,
            type=ExerciseType.CYCLING,
            metrics={"distance": 10.0, "duration": 60},
        )
        db_session.add_all([exercise1, exercise2])
        db_session.commit()

        exercises = Exercise.get_by_user(test_user.id).all()
        assert len(exercises) == 2
        assert all(e.user_id == test_user.id for e in exercises)

    def test_get_by_user_no_user(self):
        """Test get_by_user raises ValueError if user_id is missing"""
        with pytest.raises(ValueError):
            Exercise.get_by_user(None)
