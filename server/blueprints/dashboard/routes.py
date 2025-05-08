from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from collections import defaultdict


from server.blueprints.dashboard import logic
from server.models import ScheduledExercise, Goal, db, ExerciseType, ACHIEVEMENTS, CalorieIntake, BodyMeasurement, BodyMeasurementType
from server.blueprints.dashboard.forms import ScheduleExerciseForm, GoalForm

METRICS_REQUIREMENTS = {
    ExerciseType.RUNNING: [("distance_km", "km"), ("duration", "min")],
    ExerciseType.CYCLING: [("distance_km", "km"), ("duration", "min")],
    ExerciseType.SWIMMING: [("distance_m", "m"), ("duration", "min")],
    ExerciseType.WEIGHTLIFTING: [("weight_kg", "kg"), ("sets", "sets"), ("reps", "reps")],
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
        date_str = ci.created_at.strftime('%b %d')
        intake_by_date[date_str] += ci.calories  # or ci.amount, depending on your model

# Prepare data for chart
    intake_labels = list(intake_by_date.keys())
    intake_data = list(intake_by_date.values())


    if request.method == "POST":
        selected_type = request.form.get("exercise_type") or exercise_type_choices[0][0]
    else:
        selected_type = exercise_type_choices[0][0]

    schedule_form = ScheduleExerciseForm()
    goal_form = GoalForm()
    goal_form.exercise_type.choices = [(et.name, et.value) for et in ExerciseType]
    selected_type = goal_form.exercise_type.data or goal_form.exercise_type.choices[0][0]
    metrics = METRICS_REQUIREMENTS[ExerciseType[selected_type]]
    goal_form.metric.choices = [(m[0], m[0].replace("_", " ").capitalize()) for m in metrics]
    # Get latest weight (or use a default)
    latest_weight = (
        BodyMeasurement.query.filter_by(user_id=current_user.id, type=BodyMeasurementType.WEIGHT)
        .order_by(BodyMeasurement.created_at.desc())
        .first()
    )
    weight_kg = latest_weight.value if latest_weight else 70  # default 70kg
    exercises = current_user.exercises.all()

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
        print(f"DEBUG: ex_type={ex_type}, duration={duration}, weight_kg={weight_kg}")
        burned = calculate_calories_burned(ex_type, duration, weight_kg)
        print(f"DEBUG: burned={burned}")
        date_str = ex.created_at.strftime('%b %d')
        burned_by_date[date_str] += burned

    burned_labels = list(burned_by_date.keys())
    burned_data = list(burned_by_date.values())
    # --- Achievements logic ---
    # Example: fetch all exercises and measurements for this user
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
                description=goal_form.description.data,
                target_value=goal_form.target_value.data,
                current_value=0,
                unit=goal_form.unit.data
            )
            db.session.add(goal)
            db.session.commit()
            flash("Goal added!", "success")
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
        intake_labels=intake_labels,
        intake_data=intake_data,
        burned_labels=burned_labels,      # <-- add this
        burned_data=burned_data  
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
