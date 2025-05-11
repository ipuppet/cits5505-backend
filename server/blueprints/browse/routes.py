from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

from server.blueprints.browse import logic
from server.blueprints.browse.forms import (
    ExerciseForm,
    BodyMeasurementForm,
    CalorieIntakeForm,
)

browse_bp = Blueprint("browse", __name__, template_folder="templates")


@browse_bp.route("/", methods=["GET"])
@login_required
def index():
    exercise_form = ExerciseForm()
    body_measurement_form = BodyMeasurementForm()
    calorie_intake_form = CalorieIntakeForm()
    return render_template(
        "browse/index.html",
        exercise_form=exercise_form,
        exercise_types=logic.get_exercise_types(),
        exercise_metrics=logic.get_exercises_metrics(),
        body_measurement_form=body_measurement_form,
        body_measurement_types=logic.get_body_measurement_types(),
        calorie_intake_form=calorie_intake_form,
    )


@browse_bp.route("/exercise", methods=["POST"])
@login_required
def exercise():
    exercise_form = ExerciseForm()
    if exercise_form.validate_on_submit():
        try:
            achievement = logic.add_exercise_data(
                exercise_form.type.data,
                exercise_form.metrics.data,
                exercise_form.datetime,
            )
            if achievement:
                flash(
                    f"🎉 Congratulations! You reached the {achievement.milestone} milestone in {achievement.exercise_type}!",
                    "success",
                )
            flash("Exercise data added successfully!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(exercise_form.errors, "danger")
    return redirect(url_for("browse.index"))


@browse_bp.route("/body_measurement", methods=["POST"])
@login_required
def body_measurement():
    body_measurement_form = BodyMeasurementForm()
    if body_measurement_form.validate_on_submit():
        try:
            logic.add_body_measurement_data(
                body_measurement_form.type.data,
                body_measurement_form.value.data,
                body_measurement_form.datetime,
            )
            flash("Body measurement data added successfully!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(body_measurement_form.errors, "danger")
    return redirect(request.form.get("referrer", url_for("browse.index")))


@browse_bp.route("/calorie_intake", methods=["POST"])
@login_required
def calorie_intake():
    calorie_intake_form = CalorieIntakeForm()
    if calorie_intake_form.validate_on_submit():
        try:
            logic.add_calorie_intake_data(
                calorie_intake_form.calories.data,
                calorie_intake_form.description.data,
                calorie_intake_form.datetime,
            )
            flash("Calorie intake data added successfully!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(calorie_intake_form.errors, "danger")
    return redirect(url_for("browse.index"))
