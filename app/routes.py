from flask import render_template, flash, redirect, url_for, request
from app import app,db
from app.forms import RegistrationForm, LoginForm, DrinkForm, PrivateForm
from app.models import User, Drinks
from flask_login import current_user, login_user, login_required, logout_user
from flask_paginate import Pagination
from werkzeug.urls import url_parse

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
        flash('Вы зарегестрированы !')
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
			flash('Неправильное имя пользователя или пароль')
			return redirect(url_for('login'))
		login_user(user)
		flash('Успех !')
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', form = form, title = 'Вход пользователя')


#ЛОГАУТ
@app.route('/logout', methods = ['GET', 'POST'])
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
	if form.validate_on_submit():
		drink = Drinks(author = current_user)
		db.session.add(drink)
		db.session.commit()
		flash('Запись сделана в вашем профиле !')
	drinks = current_user.followed_drinks().paginate(page, app.config['POSTS_PER_PAGE'], True)
	next_url = url_for('index', page = drinks.next_num) \
		if drinks.has_next else None
	prev_url = url_for('index', page = drinks.prev_num) \
		if drinks.has_prev else None
	return render_template('index.html', title = 'Главная', form = form, drinks = drinks.items, next_url = next_url, prev_url = prev_url)

#СТРАНИЦА ПОЛЬЗОВАТЕЛЯ
@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username = username).first_or_404()
	drinks = user.drink.order_by(Drinks.drinkTime.desc()).all()
	return render_template('user.html', user = user, drinks = drinks)


#СТРАНИЦА РЕДАКТИРОВАНИЯ
@app.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
	form = PrivateForm()
	if form.validate_on_submit():
		current_user.private_stat = form.isPrivate.data
		current_user.private_stat = not(form.isntPrivate.data)
		db.session.commit()
		flash('Изменения приняты')
		return redirect(url_for('edit_profile'))
	return render_template('edit_profile.html', title = 'Редактирование профиля', form = form)


#АДМИНИСТРАТИВНАЯ СТРАНИЦА
@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin():
	if current_user.username == 'admin':
		names = User.query.all()
	else:
		flash('СТРАНИЦА ДОСТУПНА ТОЛЬКО АДМИНИСТРАТОРУ')
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
		flash('Вы не администратор')

#Функция подписки
@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username = username).first()
	if current_user == user:
		flash('Нельзя подписаться на самого себя')
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
		flash('Нельзя отписаться от самого себя')
	if user is None:
		flash(f'Пользователя {username} не существует')
	current_user.unfollow(user)
	db.session.commit()
	flash('Выпонено')
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


#comment