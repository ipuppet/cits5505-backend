from server.utils.constants import ExerciseType, EXERCISE_METRICS, BodyMeasurementType


def validate_metrics(exercise_type: ExerciseType, metrics: dict):
    required_fields = EXERCISE_METRICS.get(exercise_type, [])
    for f in required_fields:
        if f not in metrics or metrics[f] is None:
            raise ValueError(
                f"Field '{f}' is required for exercise type '{exercise_type}'"
            )
        elif isinstance(metrics[f], str):
            raise ValueError(
                f"Field '{f}' must be a number for exercise type '{exercise_type}'"
            )
        elif metrics[f] <= 0:
            raise ValueError(
                f"Field '{f}' must be greater than 0 for exercise type '{exercise_type}'"
            )
    return metrics


def validate_int(value: int):
    if not isinstance(value, int):
        raise ValueError("Value must be an integer")
    if value <= 0:
        raise ValueError("Value must be greater than 0")
    return value


def validate_float(value: float):
    if not isinstance(value, (int, float)):
        raise ValueError("Value must be a number")
    if value <= 0:
        raise ValueError("Value must be greater than 0")
    return value


def validate_body_measurement_value(type: BodyMeasurementType, value: float):
    validate_float(value)

    if type == BodyMeasurementType.WEIGHT:
        if value <= 0:
            raise ValueError("Weight must be a positive number")

    if type == BodyMeasurementType.HEIGHT:
        if value <= 0:
            raise ValueError("Height must be a positive number")

    if type == BodyMeasurementType.BODY_FAT:
        if not (0 <= value <= 100):
            raise ValueError("Body fat must be between 0 and 100")

    return value


def validate_achievement_milestone(milestone: int):
    if not isinstance(milestone, int):
        raise ValueError("Milestone must be an integer.")
    if milestone <= 0:
        raise ValueError("Milestone must be greater than 0.")
    return milestone


def validate_share_scope(scope: dict):
    if not isinstance(scope, dict):
        raise ValueError("Scope must be a dictionary.")
    scopes = [
        "exercise_types",
        "body_measurement_types",
        "achievements",
    ]
    has_scope = False
    for key in scopes:
        if key in scope:
            has_scope = True
            break
    if not has_scope:
        raise ValueError(
            f"At least one of {', '.join(scopes)} must be present in scope."
        )
    return scope
