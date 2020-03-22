from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, Length, EqualTo, DataRequired, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Имя пользователя', validators = [DataRequired()])
	email = StringField('Email', validators = [DataRequired(), Email()])
	password = PasswordField('Пароль', validators = [DataRequired()])
	password2 = PasswordField('Повторите пароль', validators = [DataRequired(), EqualTo('password')])
	submit = SubmitField('Подтвердить')

	def validate_user(self, username):
		user = User.query.filter_by(username = username.data).first()
		if user is not None:
			raise ValidationError('Данное имя пользователя занято, попробуйте другое !')

	def validate_email(self, email):
		email = User.query.filter_by(email = email.data).first()
		if email is not None:
			raise ValidationError('Данный e-mail уже используется, попробуйте другой email !')


class LoginForm(FlaskForm):
	username = StringField('Имя пользователя', validators = [DataRequired()])
	password = PasswordField('Пароль', validators = [DataRequired()])
	submit = SubmitField('Войти')
	remember_me = BooleanField('Запомни меня')


class DrinkForm(FlaskForm):
	submit = SubmitField('Выпить')


class PrivateForm(FlaskForm):
	isPrivate = BooleanField(' Скрыть статистику ')
	isntPrivate = BooleanField('Открыть статистику')
	submit = SubmitField('Принять')