from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

from server.blueprints.browse import logic
from server.blueprints.browse.forms import (
    ExerciseForm,
    BodyMeasurementForm,
    CalorieIntakeForm,
)
from server.utils.constants import ExerciseType, BodyMeasurementType

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
    form = ExerciseForm()
    if form.validate_on_submit():
        try:
            achievement = logic.add_exercise_data(
                ExerciseType[form.type.data],
                form.metrics.data,
                form.datetime,
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
        flash(str(form.errors), "danger")
    return redirect(url_for("browse.index"))


@browse_bp.route("/body_measurement", methods=["POST"])
@login_required
def body_measurement():
    form = BodyMeasurementForm()
    if form.validate_on_submit():
        try:
            logic.add_body_measurement_data(
                BodyMeasurementType[form.type.data],
                form.value.data,
                form.datetime,
            )
            flash("Body measurement data added successfully!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(str(form.errors), "danger")
    return redirect(request.form.get("referrer", url_for("browse.index")))


@browse_bp.route("/calorie_intake", methods=["POST"])
@login_required
def calorie_intake():
    form = CalorieIntakeForm()
    if form.validate_on_submit():
        try:
            logic.add_calorie_intake_data(
                form.calories.data,
                form.description.data,
                form.datetime,
            )
            flash("Calorie intake data added successfully!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(str(form.errors), "danger")
    return redirect(url_for("browse.index"))
