from flask import Blueprint, render_template, flash, redirect, url_for,g

from server.utils.decorators import login_required
from server.blueprints.browse.forms import ExerciseForm, BodyMeasurementForm
import server.blueprints.browse.logic as logic

browse_bp = Blueprint("browse", __name__, template_folder="templates")

ACHIEVEMENTS = {
    "cycling": [100, 1000, 10000],         # in km
    "running": [50, 500, 5000],            # in km
    "swimming": [10, 100, 1000],           # in km
    "weight_lifting": [1000, 10000, 100000], # in kg
    "yoga": [10, 100, 1000],               # in minutes
}

def get_user_totals(user):
    from server.models import Exercise
    totals = {
        "cycling": 0,
        "running": 0,
        "swimming": 0,
        "weight_lifting": 0,
        "yoga": 0,
    }
    exercises = g.user.exercises
    for ex in exercises:
        t = ex.type.value if hasattr(ex.type, "value") else ex.type
        if t == "cycling":
            totals["cycling"] += float(ex.metrics.get("distance_km", 0))
        elif t == "running":
            totals["running"] += float(ex.metrics.get("distance_km", 0))
        elif t == "swimming":
            totals["swimming"] += float(ex.metrics.get("distance_m", 0)) / 1000  # m to km
        elif t == "weight_lifting":
            totals["weight_lifting"] += float(ex.metrics.get("weight_kg", 0)) * int(ex.metrics.get("reps", 1)) * int(ex.metrics.get("sets", 1))
        elif t == "yoga":
            totals["yoga"] += float(ex.metrics.get("duration_min", 0))
    return totals
@browse_bp.route("/", methods=["GET"])
@login_required
def index():
    exercise_form = ExerciseForm()
    body_measurement_form = BodyMeasurementForm()
    return render_template(
        "browse/index.html",
        exercise_form=exercise_form,
        exercise_types=logic.get_exercise_types(),
        exercise_metrics=logic.get_exercises_metrics(),
        body_measurement_form=body_measurement_form,
        body_measurement_types=logic.get_body_measurement_types(),
        body_measurement_units=logic.get_body_measurement_units(),
    )


@browse_bp.route("/exercise", methods=["POST"])
@login_required
def exercise():
    exercise_form = ExerciseForm()
    if exercise_form.validate_on_submit():
        exercise_type = exercise_form.type.data
        metrics = exercise_form.metrics.data
        try:
            logic.add_exercise_data(exercise_type, metrics)
            flash("Exercise data added successfully!", "success")
             # --- Achievement check ---
            user = g.user
            totals = get_user_totals(user)
            milestones = ACHIEVEMENTS.get(exercise_type, [])
            for milestone in reversed(milestones):
                if totals[exercise_type] >= milestone:
                    flash(f"🎉 Congratulations! You reached the {milestone} milestone in {exercise_type.replace('_', ' ').capitalize()}!", "success")
                    break
        except Exception as e:
            flash(f"Error adding exercise data: {str(e)}", "danger")
    else:
        flash(exercise_form.errors, "danger")
    return redirect(url_for("browse.index"))


@browse_bp.route("/body_measurement", methods=["POST"])
@login_required
def body_measurement():
    body_measurement_form = BodyMeasurementForm()
    if body_measurement_form.validate_on_submit():
        body_measurement_type = body_measurement_form.type.data
        value = body_measurement_form.value.data
        unit = body_measurement_form.unit.data
        try:
            logic.add_body_measurement_data(body_measurement_type, value, unit)
            flash("Body measurement data added successfully!", "success")
        except Exception as e:
            flash(f"Error adding body measurement data: {str(e)}", "danger")
    else:
        flash(body_measurement_form.errors, "danger")
    return redirect(url_for("browse.index"))
