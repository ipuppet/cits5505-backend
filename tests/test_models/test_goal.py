import pytest
from server.models import Goal, User, Exercise
from server.utils.constants import ExerciseType

class TestGoalModel:
    def test_create_goal(self, session):
        """Test creating a goal"""
        user = User(username="goaluser", password="pw", email="goal@ex.com", nickname="Goal")
        session.add(user)
        session.commit()

        goal = Goal(
            user_id=user.id,
            description="Run 10km",
            exercise_type=ExerciseType.RUNNING,
            metric="distance",
            target_value=10.0
        )
        session.add(goal)
        session.commit()

        assert goal.id is not None
        assert goal.user_id == user.id
        assert goal.description == "Run 10km"
        assert goal.exercise_type == ExerciseType.RUNNING
        assert goal.metric == "distance"
        assert goal.target_value == 10.0
        assert goal.achieved is False
        assert goal.created_at is not None

    def test_current_value_and_achieved(self, session):
        """Test current_value property and achieved logic"""
        user = User(username="goaluser2", password="pw", email="goal2@ex.com", nickname="Goal2")
        session.add(user)
        session.commit()

        goal = Goal(
            user_id=user.id,
            description="Run 5km",
            exercise_type=ExerciseType.RUNNING,
            metric="distance",
            target_value=5.0
        )
        session.add(goal)
        session.commit()

        # No exercises yet
        assert goal.current_value == 0.0
        assert goal.achieved is False

        # Add an exercise with 3km (must include all required fields)
        ex1 = Exercise(
            user_id=user.id,
            type=ExerciseType.RUNNING,
            metrics={"distance": 3.0, "duration": 20}
        )
        session.add(ex1)
        session.commit()
        assert goal.current_value == 3.0
        assert goal.achieved is False

        # Add another exercise with 2.5km (must include all required fields)
        ex2 = Exercise(
            user_id=user.id,
            type=ExerciseType.RUNNING,
            metrics={"distance": 2.5, "duration": 15}
        )
        session.add(ex2)
        session.commit()
        # Now total is 5.5km, which is >= target_value
        assert goal.current_value >= goal.target_value
        assert goal.achieved is True

    def test_current_value_other_metric(self, session):
        """Test current_value with a different metric"""
        user = User(username="goaluser3", password="pw", email="goal3@ex.com", nickname="Goal3")
        session.add(user)
        session.commit()

        goal = Goal(
            user_id=user.id,
            description="Lift 100kg",
            exercise_type=ExerciseType.WEIGHTLIFTING,
            metric="weight",
            target_value=100.0
        )
        session.add(goal)
        session.commit()

        # Add weightlifting exercises (must include all required fields)
        ex1 = Exercise(
            user_id=user.id,
            type=ExerciseType.WEIGHTLIFTING,
            metrics={"weight": 40.0, "sets": 1, "reps": 10}
        )
        ex2 = Exercise(
            user_id=user.id,
            type=ExerciseType.WEIGHTLIFTING,
            metrics={"weight": 60.0, "sets": 1, "reps": 10}
        )
        session.add_all([ex1, ex2])
        session.commit()

        assert goal.current_value == 100.0
        assert goal.achieved is True