from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange

from server.models import ExerciseType, METRICS


class ScheduleExerciseForm(FlaskForm):
    day_of_week = SelectField(
        "Day",
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday"),
        ],
        validators=[DataRequired()],
    )
    exercise_type = SelectField(
        "Exercise",
        choices=[(et.name, str(et)) for et in ExerciseType],
        validators=[DataRequired()],
    )
    scheduled_time = TimeField("Time", validators=[DataRequired()])
    note = StringField("Note")
    submit = SubmitField("Add Schedule")


class GoalForm(FlaskForm):
    exercise_type = SelectField(
        "Exercise Type",
        choices=[(et.name, str(et)) for et in ExerciseType],
        validators=[DataRequired()],
    )
    metric = SelectField(
        "Metric",
        choices=[(metric, metric.capitalize()) for metric in METRICS],
        validators=[DataRequired()],
    )
    target_value = FloatField(
        "Target Value", validators=[DataRequired(), NumberRange(min=0.01)]
    )
    unit = StringField("Unit", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Add Goal")
