from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, StringField, SubmitField
from wtforms.validators import DataRequired
from server.models import ExerciseType


class ScheduleExerciseForm(FlaskForm):
    day_of_week = SelectField('Day', choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ], validators=[DataRequired()])
    exercise_type = SelectField(
        'Exercise',
        choices=[(et.name, et.value.capitalize()) for et in ExerciseType],
        validators=[DataRequired()]
    )
    scheduled_time = TimeField('Time', validators=[DataRequired()])
    note = StringField('Note')
    submit = SubmitField('Add Schedule')