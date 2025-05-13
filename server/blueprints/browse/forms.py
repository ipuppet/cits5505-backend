from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SubmitField,
    FloatField,
    StringField,
    DateField,
    TimeField,
)
from wtforms.validators import ValidationError, DataRequired, Optional
from datetime import datetime, time, date
import pytz

from server.utils.validators import validate_metrics
from server.utils.wtforms_custom import JSONField
from server.utils.constants import ExerciseType, BodyMeasurementType


class DatetimeForm(FlaskForm):
    date = DateField(
        "Date",
        format="%Y-%m-%d",
        default=date.today,
        validators=[Optional()],
    )
    time = TimeField(
        "Time",
        format="%H:%M",
        default=lambda: datetime.now().time().replace(second=0, microsecond=0),
        validators=[Optional()],
    )
    timezone = SelectField(
        "Timezone",
        choices=[],
        default="Australia/Perth",
        validators=[Optional()],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timezone.choices = self._get_timezone_choices()

    @staticmethod
    def _get_timezone_choices():
        zones = {}
        for tz in pytz.all_timezones:
            if "/" in tz:
                continent, *city = tz.split("/")
                if continent not in zones:
                    zones[continent] = []
                zones[continent].append((tz, f"{continent}/{'/'.join(city)}"))

        choices = []
        for continent, cities in sorted(zones.items()):
            choices.extend(cities)
        return choices

    @property
    def datetime(self):
        if not (self.date.data or self.time.data):
            return None

        naive_dt = datetime.combine(
            self.date.data, self.time.data if self.time.data else time(0, 0)
        )

        user_tz = pytz.timezone(self.timezone.data)
        localized_dt = user_tz.localize(naive_dt)

        # UTC
        return localized_dt.astimezone(pytz.UTC)


class ExerciseForm(DatetimeForm):
    type = SelectField(
        "Type",
        choices=[(e.name, str(e)) for e in ExerciseType],
        validators=[DataRequired()],
    )
    metrics = JSONField("metrics", validators=[Optional()])
    submit = SubmitField("Submit")

    def validate_metrics(self, metrics):
        try:
            validate_metrics(ExerciseType[self.type.data], metrics.data)
        except ValueError as e:
            raise ValidationError(str(e))


class BodyMeasurementForm(DatetimeForm):
    type = SelectField(
        "Type",
        choices=[(e.name, str(e)) for e in BodyMeasurementType],
        validators=[DataRequired()],
    )
    value = FloatField("Value", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CalorieIntakeForm(DatetimeForm):
    calories = FloatField("Calories", validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])
    submit = SubmitField("Submit")
