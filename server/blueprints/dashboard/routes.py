from flask import Blueprint, render_template, g, redirect, url_for, flash,session,request
from server.utils.decorators import login_required
from server.blueprints.dashboard.logic import fetch_weather_forecast
from server.models import ScheduledExercise, Goal, db,ExerciseType
from server.blueprints.dashboard.forms import ScheduleExerciseForm, GoalForm
from datetime import datetime, timedelta

METRICS_REQUIREMENTS = {
    ExerciseType.RUNNING: [("distance_km", "km"), ("duration", "min")],
    ExerciseType.CYCLING: [("distance_km", "km"), ("duration", "min")],
    ExerciseType.SWIMMING: [("distance_m", "m"), ("duration", "min")],
    ExerciseType.WEIGHTLIFTING: [("weight_kg", "kg"), ("sets", "sets"), ("reps", "reps")],
    ExerciseType.YOGA: [("duration", "min")],
}
dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")
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
    user = g.user

    # --- Set up choices for GoalForm before instantiation ---
    exercise_type_choices = [(et.name, et.value) for et in ExerciseType]
    selected_type = None

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

    # Set unit if metric is selected
    if request.method == "POST" and "metric" in request.form:
        for m in metrics:
            if m[0] == request.form["metric"]:
                goal_form.unit.data = m[1]

    if request.method == "POST":
        if schedule_form.submit.data and schedule_form.validate_on_submit():
            new_ex = ScheduledExercise(
                user_id=user.id,
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
                user_id=user.id,
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
    scheduled_exercises = ScheduledExercise.query.filter_by(user_id=user.id).all()
    scheduled_exercises.sort(
        key=lambda ex: (DAYS_ORDER.index(ex.day_of_week), ex.scheduled_time)
    )
    # ----------------------------------------
    goals = Goal.query.filter_by(user_id=user.id).all()
    weather_forecast = fetch_weather_forecast("Perth", days=5)
    calendar_events = [
    {
        "title": "", 
        "start": get_next_date_for_day(ex.day_of_week).strftime("%Y-%m-%d"),
        "color": "#b3d8fd",
        "extendedProps": {
            "tooltip": ex.exercise_type.value.capitalize() if hasattr(ex.exercise_type, 'value') else str(ex.exercise_type).capitalize()
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
        metrics_by_type=metrics_by_type
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