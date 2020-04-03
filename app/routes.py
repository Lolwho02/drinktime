from flask import render_template, flash, redirect, url_for, request
from app import app,db
from app.forms import RegistrationForm, LoginForm, DrinkForm, PrivateForm, PageForm, ResetPasswordForm, EmailToResetPassword
from app.email import send_reset_password_email
from app.models import User, Drinks
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from flask_babel import _

#РЕГИСТРАЦИЯ
@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data, private_stat = True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Вы зарегестрированы !'))
        return redirect(url_for('login'))
    return render_template('registration.html', form = form, title = 'Страница регистрации')

#ЛОГИН
@app.route('/login', methods = ['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash(_('Неправильное имя пользователя или пароль'))
			return redirect(url_for('login'))
		login_user(user)
		flash(_('Успех !'))
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', form = form, title = 'Вход пользователя')


#ЛОГАУТ
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


#ГЛАВНАЯ СТРАНИЦА
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
	page = request.args.get('page', 1, type = int)
	form = DrinkForm()
	current_user.det_currentstate()
	db.session.commit()
	if form.validate_on_submit():
		drink = Drinks(author = current_user)
		db.session.add(drink)
		db.session.commit()
		flash(_('Запись сделана в вашем профиле !'))
		return redirect(url_for('index'))
	drinks = current_user.followed_drinks().paginate(page, app.config['POSTS_PER_PAGE'], True)
	next_url = url_for('index', page = drinks.next_num) \
		if drinks.has_next else None
	prev_url = url_for('index', page = drinks.prev_num) \
		if drinks.has_prev else None
	page_form = PageForm()
	total_pages = drinks.pages
	drinks_pagination = drinks.iter_pages(left_edge=2, left_current=2, right_current=5, right_edge=2)
	return render_template('index.html', title = 'Главная', form = form, page = page, total_pages = total_pages,
						   drinks = drinks.items, next_url = next_url, prev_url = prev_url, page_form = page_form,
						   drinks_pagination = drinks_pagination)

#СТРАНИЦА ПОЛЬЗОВАТЕЛЯ
@app.route('/user/<username>')
@login_required
def user(username):
	page = request.args.get('page', 1, type = int)
	user = User.query.filter_by(username = username).first_or_404()
	drinks = user.drink.order_by(Drinks.drinkTime.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username = user.username, page = drinks.next_num) \
		if drinks.has_next else None
	prev_url = url_for('user', username = user.username, page = drinks.prev_num) \
		if drinks.has_prev else None
	drinks_pagination = drinks.iter_pages(left_edge=2, left_current=2, right_current=2, right_edge=2)
	return render_template('user.html', user = user, drinks = drinks.items, drinks_pagination = drinks_pagination,
						   page = page, next_url = next_url, prev_url = prev_url)


#СТРАНИЦА РЕДАКТИРОВАНИЯ
@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
	form = PrivateForm()
	if form.validate_on_submit():
		current_user.private_stat = form.isPrivate.data
		current_user.private_stat = not(form.isntPrivate.data)
		db.session.commit()
		flash(_('Изменения приняты'))
		return redirect(url_for('edit_profile'))
	return render_template('edit_profile.html', title = 'Редактирование профиля', form = form)


#АДМИНИСТРАТИВНАЯ СТРАНИЦА
@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin():
	if current_user.username == 'admin':
		names = User.query.all()
	else:
		flash(_('СТРАНИЦА ДОСТУПНА ТОЛЬКО АДМИНИСТРАТОРУ'))
		return redirect('index')
	return render_template('admin.html', names = names)

#ФУНКЦИЯ ДЛЯ УДАЛЕНИЯ(СТР АДМИНИСТРАТОРА)
@app.route('/delete/<username>')
@login_required
def delete(username):
	if current_user.username == 'admin':
		user = User.query.filter_by(username = username).first_or_404()
		db.session.delete(user)
		db.session.commit()
		return redirect(url_for('admin'))
	else:
		flash(_('Вы не администратор'))

#Функция подписки
@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username = username).first()
	if current_user == user:
		flash(_('Нельзя подписаться на самого себя'))
	else:
		current_user.follow(user)
		db.session.commit()
		flash(f'Вы успешно подписались на {username}')
	return redirect(url_for('user', username = username))

#Функция отписки
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username = username).first()
	if current_user == user:
		flash(_('Нельзя отписаться от самого себя'))
	if user is None:
		flash(f'Пользователя {username} не существует')
	current_user.unfollow(user)
	db.session.commit()
	flash(_('Выпонено'))
	return redirect(url_for('user', username = username))

#ФУНКЦИЯ ПРОСМОТРА ФОЛЛОВЕРОВ
@app.route('/user/<username>/followers')
@login_required
def followers(username):
	user = User.query.filter_by(username = username).first()
	followers = user.followers
	return render_template('followers.html', followers = followers)

#ФУНКЦИЯ ПРОСМОТРА НА КОГО ПОДПИСАН
@app.route('/user/<username>/followed')
@login_required
def followed(username):
	user = User.query.filter_by(username = username).first()
	followeds = user.followed
	return render_template('followed.html', user = user, followeds = followeds)

#ФУНКЦИЯ ВОССТАНОВЛЕНИЯ ПАРОЛЯ
@app.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = EmailToResetPassword()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None:
			send_reset_password_email(user)
			flash(_('Успешно отправлено'))
		else:
			flash(_('Пользователь с такой почтой не найден'))
	return render_template('reset_password_request.html', form = form)
@app.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = user.verify_reset_password_token(token)
	if user is None:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(self, ResetPasswordForm.password1.data)
		db.session.commit()
		flash(_('Вы успешно поменяли пароль'))
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)