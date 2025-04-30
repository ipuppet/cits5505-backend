from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import InputRequired, DataRequired

from server.utils.wtforms_custom import JSONField


class ShareForm(FlaskForm):
    receiver_id = IntegerField("receiver_id", validators=[DataRequired()])
    scope = JSONField("scope", validators=[InputRequired()])
