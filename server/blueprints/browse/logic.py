from flask import g
from sqlalchemy.exc import SQLAlchemyError
from server.models import db, Exercise, ExerciseType, METRICS_REQUIREMENTS, BodyMeasurement, BodyMeasurementType, \
    BODY_MEASUREMENT_UNITS


def get_exercise_types() -> dict:
    return {e.name: str(e) for e in ExerciseType}


def get_exercises_metrics() -> dict:
    return {
        e.name: METRICS_REQUIREMENTS[e]
        for e in ExerciseType
    }


def add_exercise_data(exercise_type, metrics):
    try:
        new_exercise = Exercise(
            user_id=g.user.id,
            type=ExerciseType[exercise_type],
            metrics=metrics,
        )
        db.session.add(new_exercise)
        db.session.commit()
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
            user_id=g.user.id,
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
