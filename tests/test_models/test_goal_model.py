from server.models import Goal, Exercise
from server.utils.constants import ExerciseType


class TestGoalModel:
    def test_create_goal(self, db_session, test_user):
        """Test creating a goal"""
        goal = Goal(
            user_id=test_user.id,
            description="Run 10km",
            exercise_type=ExerciseType.RUNNING,
            metric="distance",
            target_value=10.0,
        )
        db_session.add(goal)
        db_session.commit()

        assert goal.id is not None
        assert goal.user_id == test_user.id
        assert goal.description == "Run 10km"
        assert goal.exercise_type == ExerciseType.RUNNING
        assert goal.metric == "distance"
        assert goal.target_value == 10.0
        assert goal.achieved is False
        assert goal.created_at is not None

    def test_current_value_and_achieved(self, db_session, test_user):
        """Test current_value and achieved properties"""
        goal = Goal(
            user_id=test_user.id,
            description="Run 5km",
            exercise_type=ExerciseType.RUNNING,
            metric="distance",
            target_value=5.0,
        )
        db_session.add(goal)
        db_session.commit()

        # No exercises yet
        assert goal.current_value == 0.0
        assert goal.achieved is False

        # Add an exercise with 3km (must include all required fields)
        ex1 = Exercise(
            user_id=test_user.id,
            type=ExerciseType.RUNNING,
            metrics={"distance": 3.0, "duration": 20},
        )
        db_session.add(ex1)
        db_session.commit()
        assert goal.current_value == 3.0
        assert goal.achieved is False

        # Add another exercise with 2.5km (must include all required fields)
        ex2 = Exercise(
            user_id=test_user.id,
            type=ExerciseType.RUNNING,
            metrics={"distance": 2.5, "duration": 15},
        )
        db_session.add(ex2)
        db_session.commit()
        # Now total is 5.5km, which is >= target_value
        assert goal.current_value >= goal.target_value
        assert goal.achieved is True

    def test_current_value_other_metric(self, db_session, test_user):
        """Test current_value with a different metric"""
        goal = Goal(
            user_id=test_user.id,
            description="Lift 100kg",
            exercise_type=ExerciseType.WEIGHTLIFTING,
            metric="weight",
            target_value=100.0,
        )
        db_session.add(goal)
        db_session.commit()

        # Add weightlifting exercises (must include all required fields)
        ex1 = Exercise(
            user_id=test_user.id,
            type=ExerciseType.WEIGHTLIFTING,
            metrics={"weight": 40.0, "sets": 1, "reps": 10},
        )
        ex2 = Exercise(
            user_id=test_user.id,
            type=ExerciseType.WEIGHTLIFTING,
            metrics={"weight": 60.0, "sets": 1, "reps": 10},
        )
        db_session.add_all([ex1, ex2])
        db_session.commit()

        assert goal.current_value == 100.0
        assert goal.achieved is True
