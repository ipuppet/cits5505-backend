import requests
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user
from collections import defaultdict

from server.models import ScheduledExercise, Goal, db, BodyMeasurementType, WaterIntake
from server.utils.constants import ExerciseType, ACHIEVEMENTS


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
            sets = int(ex.metrics.get("sets"))
            reps = int(ex.metrics.get("reps"))
            duration = (sets * reps * 4) / 60  # duration in minutes
        else:
            duration = float(ex.metrics.get("duration"))
        met = met_values.get(ex.type, 6.0)  # default MET if not found
        burned = round(0.0175 * met * weight_kg * duration, 2)
        burned_by_date[str(ex.created_at.date())] += burned
    return burned_by_date


def add_schedule(exercise_type: ExerciseType, scheduled_time, day_of_week, note):
    try:
        new_se = ScheduledExercise(
            user_id=current_user.id,
            day_of_week=day_of_week,
            exercise_type=exercise_type,
            scheduled_time=scheduled_time,
            note=note,
        )
        db.session.add(new_se)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding scheduled exercise: {str(e)}")


def delete_schedule(schedule_id: int):
    try:
        schedule = db.session.get(ScheduledExercise, schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")
        db.session.delete(schedule)
        db.session.commit()
    except Exception as e:
        raise RuntimeError(f"Error deleting schedule: {str(e)}")


def edit_schedule(
    schedule_id: int,
    exercise_type: ExerciseType,
    scheduled_time,
    day_of_week,
    note,
):
    try:
        schedule = db.session.get(ScheduledExercise, schedule_id)
        schedule.day_of_week = day_of_week
        schedule.exercise_type = exercise_type
        schedule.scheduled_time = scheduled_time
        schedule.note = note
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error editing schedule: {str(e)}")


def add_goal(exercise_type: ExerciseType, metric, target_value, description):
    try:
        new_goal = Goal(
            user_id=current_user.id,
            exercise_type=exercise_type,
            metric=metric,
            target_value=target_value,
            description=description,
        )
        db.session.add(new_goal)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding goal: {str(e)}")


def delete_goal(goal_id: int):
    try:
        goal = db.session.get(Goal, goal_id)
        if not goal:
            raise ValueError("Goal not found")
        db.session.delete(goal)
        db.session.commit()
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error deleting goal: {str(e)}")


def edit_goal(
    goal_id: int,
    exercise_type: ExerciseType,
    metric,
    target_value,
    description,
):
    try:
        goal = db.session.get(Goal, goal_id).first()
        goal.exercise_type = exercise_type
        goal.metric = metric
        goal.target_value = target_value
        goal.description = description
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error editing goal: {str(e)}")


def add_water_intake(amount: float):
    try:
        new_water_intake = WaterIntake(
            user_id=current_user.id,
            amount=amount,
        )
        db.session.add(new_water_intake)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error adding water intake: {str(e)}")


def get_water_intake(target_date: datetime) -> float:
    water_intakes = current_user.water_intakes.all()
    water_today = 0
    for intake in water_intakes:
        if intake.created_at.date() == target_date.date():
            water_today += intake.amount
    return water_today


def delete_latest_water_intake():
    try:
        water_intake = current_user.water_intakes.order_by(
            WaterIntake.created_at.desc()
        ).first()
        if water_intake:
            db.session.delete(water_intake)
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise RuntimeError(f"Error deleting water intake: {str(e)}")
