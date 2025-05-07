from flask import Blueprint, render_template, flash, redirect, url_for, g
from flask_login import login_required

from server.blueprints.browse.forms import ExerciseForm, BodyMeasurementForm
import server.blueprints.browse.logic as logic

browse_bp = Blueprint("browse", __name__, template_folder="templates")


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
            achievement = logic.add_exercise_data(exercise_type, metrics)
            if achievement:
                flash(
                    f"🎉 Congratulations! You reached the {achievement.milestone} milestone in {achievement.exercise_type}!",
                    "success")
            flash("Exercise data added successfully!", "success")
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
