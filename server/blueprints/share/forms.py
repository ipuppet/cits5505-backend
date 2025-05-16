import pytz
from datetime import date, datetime, time
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField
from wtforms.fields.simple import StringField
from wtforms.validators import ValidationError, InputRequired, DataRequired

from server.utils.validators import validate_share_scope
from server.utils.wtforms_custom import JSONField


class PreviewForm(FlaskForm):
    class Meta:
        csrf = False

    scope = JSONField("scope", validators=[InputRequired()])
    start_date = DateField(
        "Start Date",
        default=date.today(),
        validators=[DataRequired()],
    )
    end_date = DateField(
        "End Date",
        default=date.today(),
        validators=[DataRequired()],
    )
    timezone = StringField("timezone", validators=[InputRequired()])

    @property
    def start_date_utc(self):
        """Returns UTC timezone start date time"""
        if not self.start_date.data or not self.timezone.data:
            return None

        timezone = pytz.timezone(self.timezone.data)
        local_datetime = datetime.combine(self.start_date.data, time(0, 0, 0))
        local_datetime = timezone.localize(local_datetime)

        return local_datetime.astimezone(pytz.UTC)

    @property
    def end_date_utc(self):
        """Returns UTC timezone end date time"""
        if not self.end_date.data or not self.timezone.data:
            return None

        timezone = pytz.timezone(self.timezone.data)
        local_datetime = datetime.combine(self.end_date.data, time(23, 59, 59))
        local_datetime = timezone.localize(local_datetime)

        return local_datetime.astimezone(pytz.UTC)

    def validate_end_date(self, end_date):
        if end_date.data < self.start_date.data:
            raise ValidationError("End date must be after start date")

    def validate_scope(self, scope):
        try:
            validate_share_scope(scope.data)
        except ValueError as e:
            raise ValidationError(str(e))


class ShareForm(PreviewForm):
    receiver_id = IntegerField("receiver_id", validators=[DataRequired()])
