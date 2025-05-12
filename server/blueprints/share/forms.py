from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField
from wtforms.validators import ValidationError, InputRequired, DataRequired

from server.utils.wtforms_custom import JSONField


class ShareForm(FlaskForm):
    receiver_id = IntegerField("receiver_id", validators=[DataRequired()])
    scope = JSONField("scope", validators=[InputRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])

    def validate_scope(self, scope):
        if not isinstance(scope.data, dict):
            raise ValidationError("Scope must be a dictionary.")
        scopes = [
            "exercise_types",
            "body_measurement_types",
            "achievements",
        ]
        has_scope = False
        for key in scopes:
            if key in scope.data:
                has_scope = True
                break
        if not has_scope:
            raise ValidationError(
                f"At least one of {', '.join(scopes)} must be present in scope."
            )
