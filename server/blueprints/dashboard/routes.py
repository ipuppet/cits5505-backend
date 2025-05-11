from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from collections import defaultdict
import json
from server.blueprints.dashboard import logic
from server.models import ScheduledExercise, Goal, db, ExerciseType, ACHIEVEMENTS, CalorieIntake, BodyMeasurement, BodyMeasurementType
from server.blueprints.dashboard.forms import ScheduleExerciseForm, GoalForm,WeightForm
from datetime import datetime, timedelta
import pytz
# Set your timezone, e.g., Perth
PERTH_TZ = pytz.timezone("Australia/Perth")
METRICS_REQUIREMENTS = {
    ExerciseType.RUNNING: [("distance_km", "km"), ("duration", "min")],
    ExerciseType.CYCLING: [("distance_km", "km"), ("duration", "min")],
    ExerciseType.SWIMMING: [("distance_m", "m"), ("duration", "min")],
    ExerciseType.WEIGHTLIFTING: [("weight_kg", "kg")],
    ExerciseType.YOGA: [("duration", "min")],
}

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

MET_VALUES = {
    "running": 9.8,
    "cycling": 7.5,
    "swimming": 8.0,
    "weight_lifting": 6.0,
    "yoga": 3.0,
}
def calculate_bmi(weight_kg, height_cm):
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)
def calculate_calories_burned(ex_type, duration_min, user_weight_kg):
    met = MET_VALUES.get(ex_type, 6.0)  # default MET if not found
    return round(0.0175 * met * user_weight_kg * duration_min, 2)
def get_next_date_for_day(day_name):
    today = datetime.now().date()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today_idx = today.weekday()
    target_idx = days.index(day_name)
    delta = (target_idx - today_idx) % 7
    return today + timedelta(days=delta)
def get_goal_current_value(user, goal):
    # Map exercise type to the metric key in metrics JSON
    metric_map = {
        "CYCLING": "distance_km",
        "RUNNING": "distance_km",
        "SWIMMING": "distance_m",
        "WEIGHTLIFTING": "weight_kg",
        "YOGA": "duration_min",
    }
    metric_key = metric_map.get(goal.exercise_type.name)
    if not metric_key:
        return 0

    # Get all exercises of this type for the user
    exercises = user.exercises.filter_by(type=goal.exercise_type).all()
    total = 0.0
    for ex in exercises:
        metrics = ex.metrics if isinstance(ex.metrics, dict) else json.loads(ex.metrics)
        value = float(metrics.get(metric_key, 0))
        total += value
    return total

@dashboard_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    # --- Set up choices for GoalForm before instantiation ---
    exercise_type_choices = [(et.name, et.value) for et in ExerciseType]
    selected_type = None
    calorie_intakes = CalorieIntake.query.filter_by(user_id=current_user.id).order_by(CalorieIntake.created_at.asc()).all()

# Group and sum by date
    intake_by_date = defaultdict(int)
    for ci in calorie_intakes:
    # Convert to Perth timezone if not already aware
        if ci.created_at.tzinfo is None:
            ci_time = pytz.utc.localize(ci.created_at).astimezone(PERTH_TZ)
        else:
            ci_time = ci.created_at.astimezone(PERTH_TZ)
        date_str = ci_time.strftime('%b %d')
        intake_by_date[date_str] += ci.calories  # or ci.amount, depending on your model
    intake_labels = list(intake_by_date.keys())
    intake_data = list(intake_by_date.values())

    weight_form = WeightForm()
    schedule_form = ScheduleExerciseForm()
    goal_form = GoalForm()
    goal_form.exercise_type.choices = [(et.name, et.value) for et in ExerciseType]

# Use POSTed value if present, else use form data, else default
    # Always get the selected type from form data, POST, or default
    selected_type = (
        request.form.get("exercise_type")
        or goal_form.exercise_type.data
        or goal_form.exercise_type.choices[0][0]
    )
    metrics = METRICS_REQUIREMENTS[ExerciseType[selected_type]]
    goal_form.metric.choices = [(m[0], m[0][0].upper() + m[0][1:]) for m in metrics]    # Get latest weight (or use a default)
    latest_weight = (
        BodyMeasurement.query.filter_by(user_id=current_user.id, type=BodyMeasurementType.WEIGHT)
        .order_by(BodyMeasurement.created_at.desc())
        .first()
    )
    weight_kg = latest_weight.value if latest_weight else 70  # default 70kg
    exercises = current_user.exercises.all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    for goal in goals:
        goal.current_value = get_goal_current_value(current_user, goal)

# Calculate and sum calories burned per day
    burned_by_date = defaultdict(float)
    for ex in exercises:
        ex_type = ex.type.value if hasattr(ex.type, "value") else str(ex.type)
        if ex_type == "weight_lifting":
        # Estimate duration: assume 4 seconds per rep
            sets = int(ex.metrics.get("sets", 0))
            reps = int(ex.metrics.get("reps", 0))
            duration = (sets * reps * 4) / 60  # duration in minutes
        else:
            duration = float(ex.metrics.get("duration_min", 0))
        burned = calculate_calories_burned(ex_type, duration, weight_kg)
        if ex.created_at.tzinfo is None:
            ex_time = pytz.utc.localize(ex.created_at).astimezone(PERTH_TZ)
        else:
            ex_time = ex.created_at.astimezone(PERTH_TZ)
        date_str = ex_time.strftime('%b %d')
        burned_by_date[date_str] += burned

    burned_labels = list(burned_by_date.keys())
    burned_data = list(burned_by_date.values())
    # --- Achievements logic ---
    achievements = logic.get_achievements_dict()

    # Set unit if metric is selected
    if request.method == "POST" and "metric" in request.form:
        for m in metrics:
            if m[0] == request.form["metric"]:
                goal_form.unit.data = m[1]

    if request.method == "POST":
        if schedule_form.submit.data and schedule_form.validate_on_submit():
            new_ex = ScheduledExercise(
                user_id=current_user.id,
                day_of_week=schedule_form.day_of_week.data,
                exercise_type=schedule_form.exercise_type.data,
                scheduled_time=schedule_form.scheduled_time.data,
                note=schedule_form.note.data
            )
            db.session.add(new_ex)
            db.session.commit()
            flash('Exercise scheduled!', 'success')
            return redirect(url_for('dashboard.index'))
        elif goal_form.submit.data and goal_form.validate_on_submit():
            goal = Goal(
                user_id=current_user.id,
                exercise_type=goal_form.exercise_type.data,
                metric=goal_form.metric.data,
                description=goal_form.description.data,
                target_value=goal_form.target_value.data,
                current_value=0,
                unit=goal_form.unit.data
            )
            db.session.add(goal)
            db.session.commit()
            flash("Goal added!", "success")
            print(goal_form.errors)  # Add this line to see validation errors
            return redirect(url_for("dashboard.index"))

    # --- sorting date  here ---
    DAYS_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    scheduled_exercises = current_user.scheduled_exercises.all()
    scheduled_exercises.sort(
        key=lambda ex: (DAYS_ORDER.index(ex.day_of_week), ex.scheduled_time)
    )
    # ----------------------------------------
    goals = current_user.goals.all()
    weather_forecast = logic.fetch_weather_forecast("Perth", days=5)
    calendar_events = [
        {
            "title": "",
            "start": get_next_date_for_day(ex.day_of_week).strftime("%Y-%m-%d"),
            "color": "#b3d8fd",
            "extendedProps": {
                "tooltip": ex.exercise_type.value.capitalize() if hasattr(ex.exercise_type, 'value') else str(
                    ex.exercise_type).capitalize()
            }
        }
        for ex in scheduled_exercises
    ]
   
    metrics_by_type = {et.name: METRICS_REQUIREMENTS[et] for et in ExerciseType}
    # Get all weight measurements for the current user
    weight_measurements = (
        BodyMeasurement.query
        .filter_by(user_id=current_user.id, type=BodyMeasurementType.WEIGHT)
        .order_by(BodyMeasurement.created_at.asc())
        .all()
    )
    weight_labels = []
    weight_by_date = {}
    for bm in weight_measurements:
    # Convert to Perth timezone if not already aware
        if bm.created_at.tzinfo is None:
         bm_time = pytz.utc.localize(bm.created_at).astimezone(PERTH_TZ)
        else:
            bm_time = bm.created_at.astimezone(PERTH_TZ)
        label = bm_time.strftime('%b %d')
        weight_labels.append(label)
        weight_by_date[label] = bm.value
# Build last 14 days labels (to match getLast14DaysLabels)
    today = datetime.now(PERTH_TZ)    
     # Get latest weight
    latest_weight = (
    BodyMeasurement.query.filter_by(user_id=current_user.id, type=BodyMeasurementType.WEIGHT)
    .order_by(BodyMeasurement.created_at.desc())
    .first()
    )
    # Get latest height
    latest_height = (
    BodyMeasurement.query.filter_by(user_id=current_user.id, type=BodyMeasurementType.HEIGHT)
    .order_by(BodyMeasurement.created_at.desc())
    .first()
    )
    weight_kg = latest_weight.value if latest_weight else None
    height_cm = latest_height.value if latest_height else None

    bmi = calculate_bmi(weight_kg, height_cm)
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
    weight_data = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        label = day.strftime('%b %d')
        weight_labels.append(label)
    # Only show value if entry exists for that day, else null
        value = weight_by_date.get(label, None)
        weight_data.append(value)
        print("Latest height:", latest_height.value if latest_height else None)        
        print("Latest weight:", latest_weight.value if latest_weight else None)
        print("BMI:", bmi)
    return render_template(
        "dashboard/index.html",
        weather_forecast=weather_forecast,
        scheduled_exercises=scheduled_exercises,
        goals=goals,
        calendar_events=calendar_events,
        now=datetime.now(),
        form=schedule_form,
        goal_form=goal_form,
        metrics_by_type=metrics_by_type,
        achievements=achievements,
        ACHIEVEMENTS=logic.get_all_achievements(),
        calorie_intakes=calorie_intakes,
        exercises=exercises,
        bmi=bmi,
        bmi_category=bmi_category,
        intake_labels=intake_labels,
        intake_data=intake_data,
        burned_labels=burned_labels,     
        burned_data=burned_data,
        weight_labels=weight_labels,
        weight_data=weight_data,
        weight_form=weight_form
        
        
        
    )


@dashboard_bp.route("/delete_schedule/<int:id>", methods=["POST"])
@login_required
def delete_schedule(id):
    ex = ScheduledExercise.query.get_or_404(id)
    user_id = session.get("user_id")
    if ex.user_id != user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.index'))
    db.session.delete(ex)
    db.session.commit()
    flash("Schedule deleted.", "success")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route("/edit_schedule/<int:id>", methods=["POST"])
@login_required
def edit_schedule(id):
    ex = ScheduledExercise.query.get_or_404(id)
    user_id = session.get("user_id")
    if ex.user_id != user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.index'))
    ex.day_of_week = request.form["day_of_week"]
    ex.exercise_type = request.form["exercise_type"]
    ex.scheduled_time = datetime.strptime(request.form["scheduled_time"], "%H:%M").time()
    ex.note = request.form["note"]
    db.session.commit()
    flash("Schedule updated.", "success")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route("/delete_goal/<int:id>", methods=["POST"])
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    user_id = session.get("user_id")
    if goal.user_id != user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.index'))
    db.session.delete(goal)
    db.session.commit()
    flash("Goal deleted.", "success")
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route("/edit_goal/<int:id>", methods=["POST"])
@login_required
def edit_goal(id):
    goal = Goal.query.get_or_404(id)
    user_id = session.get("user_id")
    if goal.user_id != user_id:
        flash("Unauthorized", "danger")
        return redirect(url_for('dashboard.index'))
    goal.description = request.form["description"]
    goal.exercise_type = request.form["exercise_type"]
    goal.metric = request.form["metric"]
    goal.target_value = request.form["target_value"]
    goal.unit = request.form["unit"]
    db.session.commit()
    flash("Goal updated.", "success")
    return redirect(url_for('dashboard.index'))
@dashboard_bp.route("/edit_weight", methods=["POST"])
@login_required
def edit_weight():
    form = WeightForm()
    if form.validate_on_submit():
        new_weight = BodyMeasurement(
            user_id=current_user.id,
            type=BodyMeasurementType.WEIGHT,
            value=form.value.data,
            unit="kg",  # <-- Add this line
            created_at=form.date.data,
        )
        db.session.add(new_weight)
        db.session.commit()
    return redirect(url_for("dashboard.index"))




