from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Email


class RegistrationForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    nickname = StringField("nickname", validators=[Optional()])
    password = PasswordField(
        "password",
        validators=[
            DataRequired(),
            Length(
                min=6,
                message="Password must be at least 6 characters long",
            ),
        ],
    )
    email = StringField("email", validators=[Email()])
