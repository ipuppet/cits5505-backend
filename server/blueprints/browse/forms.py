from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, FloatField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Optional

from server.utils.wtforms_custom import JSONField
from server.models import ExerciseType, BodyMeasurementType, BODY_MEASUREMENT_UNITS


class ExerciseForm(FlaskForm):
    type = SelectField("Type", choices=[(e.name, str(e)) for e in ExerciseType],
                       validators=[DataRequired()])
    metrics = JSONField("metrics", validators=[Optional()])
    submit = SubmitField("Submit")

    def validate_metrics(self, field):
        if not field.data:
            raise ValidationError("Metrics cannot be empty.")


class BodyMeasurementForm(FlaskForm):
    type = SelectField("Type", choices=[(e.name, str(e)) for e in BodyMeasurementType],
                       validators=[DataRequired()])
    value = FloatField("Value", validators=[DataRequired()])
    unit = SelectField(
        "Unit",
        choices=[(unit, unit) for unit in sorted({
            unit for units in BODY_MEASUREMENT_UNITS.values()
            for unit in units
        })],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")
