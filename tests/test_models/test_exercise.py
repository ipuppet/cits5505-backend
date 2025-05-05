import pytest
from server.models import Exercise, ExerciseType


class TestExerciseModel:
    @pytest.mark.parametrize(
        "exercise_type,valid_metrics",
        [
            (ExerciseType.RUNNING, {"distance_km": 5.0, "duration_min": 30}),
            (ExerciseType.WEIGHTLIFTING, {"weight_kg": 50.0, "sets": 3, "reps": 12}),
            (ExerciseType.YOGA, {"duration_min": 45}),
        ],
    )
    def test_valid_exercise_creation(self, session, exercise_type, valid_metrics):
        """Test valid exercise creation with correct metrics"""
        exercise = Exercise(user_id=1, type=exercise_type, metrics=valid_metrics)
        session.add(exercise)
        session.commit()

        assert exercise.id is not None
        assert exercise.created_at is not None
        assert exercise.metrics == valid_metrics

    @pytest.mark.parametrize(
        "exercise_type,invalid_metrics",
        [
            # Single field missing
            (ExerciseType.RUNNING, {"duration_min": 30}),
            (ExerciseType.CYCLING, {"distance_km": 10}),
            (ExerciseType.SWIMMING, {"distance_m": 50}),
            (ExerciseType.WEIGHTLIFTING, {"weight_kg": 50, "sets": 3}),
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
        with pytest.raises(ValueError) as excinfo:
            Exercise(user_id=1, type=exercise_type, metrics=invalid_metrics)

    def test_get_method(self, session):
        """Test retrieval of exercise by ID"""
        # Create test exercise
        exercise = Exercise(
            user_id=1,
            type=ExerciseType.RUNNING,
            metrics={"distance_km": 5.0, "duration_min": 30},
        )
        session.add(exercise)
        session.commit()

        # Test valid get
        result = Exercise.get(exercise.id)
        assert result.id == exercise.id

        # Test invalid ID
        with pytest.raises(ValueError):
            Exercise.get("invalid_id")
