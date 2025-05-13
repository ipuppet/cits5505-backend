from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField
from wtforms.validators import ValidationError, InputRequired, DataRequired

from server.utils.validators import validate_scope
from server.utils.wtforms_custom import JSONField


class ShareForm(FlaskForm):
    receiver_id = IntegerField("receiver_id", validators=[DataRequired()])
    scope = JSONField("scope", validators=[InputRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])

    def validate_scope(self, scope):
        try:
            validate_scope(scope)
        except ValueError as e:
            raise ValidationError(str(e))
