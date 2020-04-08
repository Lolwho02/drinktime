from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, Length, EqualTo, DataRequired, ValidationError
from app.models import User
from flask_babel import lazy_gettext as _l

class RegistrationForm(FlaskForm):
	username = StringField(_l('Имя пользователя'), validators = [DataRequired()])
	email = StringField(_l('Email'), validators = [DataRequired(), Email()])
	password = PasswordField(_l('Пароль'), validators = [DataRequired()])
	password2 = PasswordField(_l('Повторите пароль'), validators = [DataRequired(), EqualTo('password')])
	submit = SubmitField(_l('Подтвердить'))

	def validate_user(self, username):
		user = User.query.filter_by(username = username.data).first()
		if user is not None:
			raise ValidationError('Данное имя пользователя занято, попробуйте другое !')

	def validate_email(self, email):
		email = User.query.filter_by(email = email.data).first()
		if email is not None:
			raise ValidationError('Данный e-mail уже используется, попробуйте другой email !')



class DrinkForm(FlaskForm):
	submit = SubmitField(_l('Выпить'))


class PageForm(FlaskForm):
	page = StringField('Номер страницы', validators = [DataRequired()])
	submit = SubmitField('Перейти')

class PrivateForm(FlaskForm):
	isPrivate = BooleanField(_l(' Скрыть статистику '))
	isntPrivate = BooleanField(_l('Открыть статистику'))
	submit = SubmitField(_l('Принять'))