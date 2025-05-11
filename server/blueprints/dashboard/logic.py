import requests
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user
from collections import defaultdict

from server.models import (
    ScheduledExercise,
    Goal,
    db,
    ExerciseType,
    ACHIEVEMENTS,
    BodyMeasurementType,
)


def fetch_weather_forecast(city, days=5):
    api_key = "5118a8c67aec70333dac3704a6b65bb6"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "units": "metric", "appid": api_key}
    resp = requests.get(url, params=params, timeout=5)
    data = resp.json()

    weather_forecast = []
    seen_dates = set()
    for item in data.get("list", []):
        date_str = datetime.fromtimestamp(item["dt"], tz=timezone.utc).strftime("%a %d")
        if date_str not in seen_dates and len(weather_forecast) < days:
            weather_forecast.append(
                {
                    "date": date_str,
                    "icon_url": f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                    "temp": round(item["main"]["temp"]),
                    "description": item["weather"][0]["main"],
                }
            )
            seen_dates.add(date_str)
    return weather_forecast


def get_all_achievements() -> dict:
    return ACHIEVEMENTS


def get_achievements_by_type() -> dict:
    achievements = {}
    for achievement in current_user.achievements:
        if achievement.exercise_type not in achievements:
            achievements[achievement.exercise_type] = []
        achievements[achievement.exercise_type].append(achievement.milestone)
    return achievements


def get_weight():
    latest_weight = current_user.body_measurements.filter_by(
        type=BodyMeasurementType.WEIGHT
    ).first()
    return latest_weight.value if latest_weight else None


def get_height():
    latest_height = current_user.body_measurements.filter_by(
        type=BodyMeasurementType.HEIGHT
    ).first()
    return latest_height.value if latest_height else None


def get_bmi():
    weight_kg = get_weight()
    height_cm = get_height()
    if not weight_kg or not height_cm:
        return None, None
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m**2), 1)

    bmi_category = None
    if bmi:
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obesity"
    return bmi, bmi_category


def get_burned_calories():
    weight_kg = get_weight()
    if not weight_kg:
        weight_kg = 70

    met_values = {
        ExerciseType.RUNNING: 9.8,
        ExerciseType.CYCLING: 7.5,
        ExerciseType.SWIMMING: 8.0,
        ExerciseType.WEIGHTLIFTING: 6.0,
        ExerciseType.YOGA: 3.0,
    }

    burned_by_date = defaultdict(float)
    for ex in current_user.exercises.all():
        if ex.type == ExerciseType.WEIGHTLIFTING:
            # Estimate duration: assume 4 seconds per rep
            sets = int(ex.metrics.get("sets", 0))
            reps = int(ex.metrics.get("reps", 0))
            duration = (sets * reps * 4) / 60  # duration in minutes
        else:
            duration = float(ex.metrics.get("duration", 0))
        met = met_values.get(ex.type, 6.0)  # default MET if not found
        burned = round(0.0175 * met * weight_kg * duration, 2)
        burned_by_date[str(ex.created_at.date())] += burned
    return burned_by_date


def add_schedule(exercise_type, scheduled_time, day_of_week, note):
    try:
        new_se = ScheduledExercise(
            user_id=current_user.id,
            day_of_week=day_of_week,
            exercise_type=ExerciseType[exercise_type],
            scheduled_time=scheduled_time,
            note=note,
        )
        db.session.add(new_se)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding scheduled exercise: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")


def delete_schedule(schedule_id):
    try:
        db.session.delete(ScheduledExercise.get(schedule_id))
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error deleting schedule: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")


def edit_schedule(schedule_id, exercise_type, scheduled_time, day_of_week, note):
    try:
        schedule = ScheduledExercise.get(schedule_id)
        schedule.day_of_week = day_of_week
        schedule.exercise_type = ExerciseType[exercise_type]
        schedule.scheduled_time = scheduled_time
        schedule.note = note
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error editing schedule: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")


def add_goal(exercise_type, metric, target_value, description):
    try:
        new_goal = Goal(
            user_id=current_user.id,
            exercise_type=ExerciseType[exercise_type],
            metric=metric,
            target_value=target_value,
            description=description,
        )
        db.session.add(new_goal)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding goal: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")


def delete_goal(goal_id):
    try:
        db.session.delete(Goal.get(goal_id))
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error deleting goal: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")


def edit_goal(goal_id, exercise_type, metric, target_value, description):
    try:
        goal = Goal.get(goal_id)
        goal.exercise_type = ExerciseType[exercise_type]
        goal.metric = metric
        goal.target_value = target_value
        goal.description = description
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error editing goal: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Unexpected error: {str(e)}")
