from flask import Blueprint, render_template, g, redirect, url_for, flash,session
from server.utils.decorators import login_required
from server.blueprints.dashboard.logic import fetch_weather_forecast
from server.models import ScheduledExercise, Goal, db
from server.blueprints.dashboard.forms import ScheduleExerciseForm
from datetime import datetime



dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")


@dashboard_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user = g.user
    form = ScheduleExerciseForm()
    if form.validate_on_submit():
        new_ex = ScheduledExercise(
            user_id=user.id,
            day_of_week=form.day_of_week.data,
            exercise_type=form.exercise_type.data,
            scheduled_time=form.scheduled_time.data,
            note=form.note.data
        )
        db.session.add(new_ex)
        db.session.commit()
        flash('Exercise scheduled!', 'success')
        return redirect(url_for('dashboard.index'))

    scheduled_exercises = ScheduledExercise.query.filter_by(user_id=user.id).all()
    goals = Goal.query.filter_by(user_id=user.id).all()
    weather_forecast = fetch_weather_forecast("Perth", days=5)
    calendar_events = [
        {
            "title": ex.exercise_type.value if hasattr(ex.exercise_type, 'value') else ex.exercise_type,
            "start": ex.scheduled_time.strftime("%Y-%m-%d"),
            "color": "#b3d8fd"
        }
        for ex in scheduled_exercises
    ]
    return render_template(
        "dashboard/index.html",
        weather_forecast=weather_forecast,
        scheduled_exercises=scheduled_exercises,
        goals=goals,
        calendar_events=calendar_events,
        form=form
    )
    
    
from flask import request

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