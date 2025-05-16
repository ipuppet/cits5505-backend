from enum import Enum


def to_camel_case(snake: str, space: bool = False) -> str:
    replace_to = " " if space else ""
    return snake.replace("_", replace_to).title()


class ExerciseType(Enum):
    CYCLING = "cycling"
    RUNNING = "running"
    SWIMMING = "swimming"
    WEIGHTLIFTING = "weight_lifting"
    YOGA = "yoga"

    def __str__(self):
        return to_camel_case(self.value, True)


class BodyMeasurementType(Enum):
    WEIGHT = "weight"
    HEIGHT = "height"
    BODY_FAT = "body_fat"

    def __str__(self):
        return to_camel_case(self.value, True)


EXERCISE_METRICS = {
    ExerciseType.CYCLING: ["distance", "duration"],  # in meters and minutes
    ExerciseType.RUNNING: ["distance", "duration"],
    ExerciseType.SWIMMING: ["distance", "duration"],
    ExerciseType.WEIGHTLIFTING: ["weight", "sets", "reps"],  # in kg
    ExerciseType.YOGA: ["duration"],
}
GOAL_METRICS = [
    "distance",
    "duration",
    "weight",
]

# integer values
ACHIEVEMENTS = {
    ExerciseType.CYCLING: [50000, 100000, 200000],  # in m
    ExerciseType.RUNNING: [10000, 50000, 100000],
    ExerciseType.SWIMMING: [10000, 50000, 100000],
    ExerciseType.WEIGHTLIFTING: [50, 100, 200],  # in kg
    ExerciseType.YOGA: [100, 500, 1000],  # in minutes
}
