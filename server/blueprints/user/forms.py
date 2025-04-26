from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Email


class PasswordForm(FlaskForm):
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


class EmailForm(FlaskForm):
    email = StringField("email", validators=[Optional(), Email()])


class UserInfoForm(EmailForm):
    username = StringField("username", validators=[Optional()])
    nickname = StringField("nickname", validators=[Optional()])


class LoginForm(PasswordForm, EmailForm):
    remember_me = BooleanField("remember_me", validators=[Optional()])


class RegistrationForm(PasswordForm, UserInfoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email.validators = [DataRequired(), Email()]
        self.username.validators = [DataRequired()]

        if not self.nickname.data and self.username.data:
            self.nickname.data = self.username.data
