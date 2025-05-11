from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    DateField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, Optional, Email


class PasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=6,
                message="Password must be at least 6 characters long",
            ),
        ],
    )


class EmailForm(FlaskForm):
    email = StringField("Email", validators=[Optional(), Email()])


class UserInfoForm(EmailForm):
    username = StringField("Username", validators=[Optional()])
    nickname = StringField("Nickname", validators=[Optional()])
    date_of_birth = DateField(
        "Date of Birth", format="%Y-%m-%d", validators=[Optional()]
    )
    sex = SelectField(
        "Sex",
        choices=[
            ("", "Select"),
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )


class LoginForm(PasswordForm, EmailForm):
    remember_me = BooleanField("Remember Me", validators=[Optional()])


class RegistrationForm(PasswordForm, UserInfoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email.validators = [DataRequired(), Email()]
        self.username.validators = [DataRequired()]

        if not self.nickname.data and self.username.data:
            self.nickname.data = self.username.data
