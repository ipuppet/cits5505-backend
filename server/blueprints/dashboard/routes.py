from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

from server.blueprints.browse.forms import BodyMeasurementForm
from server.blueprints.dashboard import logic
from server.models import ExerciseType, METRICS_REQUIREMENTS
from server.blueprints.dashboard.forms import ScheduleExerciseForm, GoalForm

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    body_measurement_form = BodyMeasurementForm()
    schedule_form = ScheduleExerciseForm()
    goal_form = GoalForm()

    weather_forecast = logic.fetch_weather_forecast("Perth", days=5)
    bmi, bmi_category = logic.get_bmi()
    return render_template(
        "dashboard/index.html",
        now=datetime.now(),
        body_measurement_form=body_measurement_form,
        schedule_form=schedule_form,
        goal_form=goal_form,
        weather_forecast=weather_forecast,
        bmi=bmi,
        bmi_category=bmi_category,
        metrics_by_type={e.name: METRICS_REQUIREMENTS[e] for e in ExerciseType},
        achievements_by_type=logic.get_achievements_by_type(),
        all_achievements=logic.get_all_achievements(),
        burned_by_date=logic.get_burned_calories(),
    )


@dashboard_bp.route("/add_schedule", methods=["POST"])
@login_required
def add_schedule():
    form = ScheduleExerciseForm()
    if form.validate_on_submit():
        try:
            logic.add_schedule(
                form.exercise_type.data,
                form.scheduled_time.data,
                form.day_of_week.data,
                form.note.data,
            )
            flash("Exercise scheduled!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(form.errors, "danger")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/add_goal", methods=["POST"])
@login_required
def add_goal():
    form = GoalForm()
    if form.validate_on_submit():
        try:
            logic.add_goal(
                form.exercise_type.data,
                form.metric.data,
                form.target_value.data,
                form.description.data,
            )
            flash("Goal added!", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        flash(form.errors, "danger")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/delete_schedule/<int:id>", methods=["POST"])
@login_required
def delete_schedule(id):
    try:
        logic.delete_schedule(id)
        flash("Schedule deleted.", "success")
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/edit_schedule/<int:id>", methods=["POST"])
@login_required
def edit_schedule(id):
    form = ScheduleExerciseForm()
    try:
        logic.edit_schedule(
            id,
            form.exercise_type.data,
            form.scheduled_time.data,
            form.day_of_week.data,
            form.note.data,
        )
        flash("Schedule updated.", "success")
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/delete_goal/<int:id>", methods=["POST"])
@login_required
def delete_goal(id):
    try:
        logic.delete_goal(id)
        flash("Goal deleted.", "success")
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/edit_goal/<int:id>", methods=["POST"])
@login_required
def edit_goal(id):
    form = GoalForm()
    try:
        logic.edit_goal(
            id,
            form.exercise_type.data,
            form.metric.data,
            form.target_value.data,
            form.description.data,
        )
        flash("Goal updated.", "success")
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard.index"))
    flash("Goal updated.", "success")
    return redirect(url_for("dashboard.index"))
