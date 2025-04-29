from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,DateField, SelectField, FloatField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange


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
    date_of_birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[DataRequired()])
    sex = SelectField("Sex", choices=[('', 'Select'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    height = FloatField("Height (cm)", validators=[DataRequired(), NumberRange(min=0, max=300)])
    weight = FloatField("Weight (kg)", validators=[DataRequired(), NumberRange(min=0, max=500)])


class LoginForm(PasswordForm, EmailForm):
    remember_me = BooleanField("remember_me", validators=[Optional()])


class RegistrationForm(PasswordForm, UserInfoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.email.validators = [DataRequired(), Email()]
        self.username.validators = [DataRequired()]
        

        if not self.nickname.data and self.username.data:
            self.nickname.data = self.username.data
