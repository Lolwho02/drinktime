from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_babel import lazy_gettext as _l


class LoginForm(FlaskForm):
	username = StringField(_l('Имя пользователя'), validators = [DataRequired()])
	password = PasswordField(_l('Пароль'), validators = [DataRequired()])
	submit = SubmitField(_l('Войти'))
	remember_me = BooleanField(_l('Запомни меня'))


class EmailToResetPassword(FlaskForm):
	email = StringField(_l('Email'), validators = [DataRequired(), Email()])
	submit = SubmitField(_l('Принять'))


class ResetPasswordForm(FlaskForm):
	password1 = PasswordField(_l('Пароль'), validators = [DataRequired()])
	password2 = PasswordField(_l('Подтвердите пароль'), validators = [EqualTo('password1')])
	submit = SubmitField(_l('Принять'))