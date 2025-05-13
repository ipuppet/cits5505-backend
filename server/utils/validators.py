from server.utils.constants import ExerciseType, EXERCISE_METRICS


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


def validate_scope(scope: dict):
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
