from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from server.models import db, Exercise, ExerciseType, METRICS_REQUIREMENTS, BodyMeasurement, BodyMeasurementType, \
    BODY_MEASUREMENT_UNITS, ACHIEVEMENTS, Achievement


def get_exercise_types() -> dict:
    return {e.name: str(e) for e in ExerciseType}


def get_exercises_metrics() -> dict:
    return {
        e.name: METRICS_REQUIREMENTS[e]
        for e in ExerciseType
    }


def add_exercise_data(exercise_type, metrics) -> Achievement | None:
    try:
        exercise_type = ExerciseType[exercise_type]
        new_exercise = Exercise(
            user_id=current_user.id,
            type=exercise_type,
            metrics=metrics,
        )
        db.session.add(new_exercise)
        # Check achievements
        exercises = current_user.exercises.filter_by(type=exercise_type).all()
        total = sum(float(ex.metrics.get(METRICS_REQUIREMENTS[exercise_type][0], 0)) for ex in exercises)
        achievements = current_user.achievements.filter_by(exercise_type=exercise_type).all()
        new_achievement = None
        for milestone in ACHIEVEMENTS[exercise_type]:
            if total >= milestone and not any(a.milestone == milestone for a in achievements):
                new_achievement = Achievement(
                    user_id=current_user.id,
                    exercise_type=exercise_type,
                    milestone=milestone,
                )
                db.session.add(new_achievement)
        db.session.commit()
        return new_achievement
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding exercise data: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")


def get_body_measurement_types() -> dict:
    return {e.name: str(e) for e in BodyMeasurementType}


def get_body_measurement_units() -> dict:
    return {
        e.name: BODY_MEASUREMENT_UNITS[e]
        for e in BodyMeasurementType
    }


def add_body_measurement_data(body_measurement_type, value, unit):
    try:
        new_body_measurement = BodyMeasurement(
            user_id=current_user.id,
            type=BodyMeasurementType[body_measurement_type],
            value=value,
            unit=unit,
        )
        db.session.add(new_body_measurement)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding body measurement data: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")
