from flask import render_template, flash, redirect, url_for, request, current_app
from app.main import main
from app import db
from app.main.forms import RegistrationForm, DrinkForm, PrivateForm, PageForm
from app.models import User, Drinks
from flask_login import current_user, login_required
from flask_babel import _

#РЕГИСТРАЦИЯ
@main.route('/registration', methods = ['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data, private_stat = True)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Вы зарегестрированы !'))
        return redirect(url_for('auth.login'))
    return render_template('registration.html', form = form, title = 'Страница регистрации')

#ГЛАВНАЯ СТРАНИЦА
@main.route('/', methods = ['GET', 'POST'])
@main.route('/index', methods = ['GET', 'POST'])
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
		return redirect(url_for('main.index'))
	drinks = current_user.followed_drinks().paginate(page, current_app.config['POSTS_PER_PAGE'], True)
	next_url = url_for('main.index', page = drinks.next_num) \
		if drinks.has_next else None
	prev_url = url_for('main.index', page = drinks.prev_num) \
		if drinks.has_prev else None
	page_form = PageForm()
	total_pages = drinks.pages
	drinks_pagination = drinks.iter_pages(left_edge=2, left_current=2, right_current=5, right_edge=2)
	return render_template('index.html', title = 'Главная', form = form, page = page, total_pages = total_pages,
						   drinks = drinks.items, next_url = next_url, prev_url = prev_url, page_form = page_form,
						   drinks_pagination = drinks_pagination)

#СТРАНИЦА ПОЛЬЗОВАТЕЛЯ
@main.route('/user/<username>')
@login_required
def user(username):
	page = request.args.get('page', 1, type = int)
	user = User.query.filter_by(username = username).first_or_404()
	drinks = user.drink.order_by(Drinks.drinkTime.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.user', username = user.username, page = drinks.next_num) \
		if drinks.has_next else None
	prev_url = url_for('main.user', username = user.username, page = drinks.prev_num) \
		if drinks.has_prev else None
	drinks_pagination = drinks.iter_pages(left_edge=2, left_current=2, right_current=2, right_edge=2)
	return render_template('user.html', user = user, drinks = drinks.items, drinks_pagination = drinks_pagination,
						   page = page, next_url = next_url, prev_url = prev_url)


#СТРАНИЦА РЕДАКТИРОВАНИЯ
@main.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
	form = PrivateForm()
	if form.validate_on_submit():
		current_user.private_stat = form.isPrivate.data
		current_user.private_stat = not(form.isntPrivate.data)
		db.session.commit()
		flash(_('Изменения приняты'))
		return redirect(url_for('main.edit_profile'))
	return render_template('edit_profile.html', title = 'Редактирование профиля', form = form)


#АДМИНИСТРАТИВНАЯ СТРАНИЦА
@main.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin():
	if current_user.username == 'admin':
		names = User.query.all()
	else:
		flash(_('СТРАНИЦА ДОСТУПНА ТОЛЬКО АДМИНИСТРАТОРУ'))
		return redirect('main.index')
	return render_template('admin.html', names = names)

#ФУНКЦИЯ ДЛЯ УДАЛЕНИЯ(СТР АДМИНИСТРАТОРА)
@main.route('/delete/<username>')
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
@main.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username = username).first()
	if current_user == user:
		flash(_('Нельзя подписаться на самого себя'))
	else:
		current_user.follow(user)
		db.session.commit()
		flash(f'Вы успешно подписались на {username}')
	return redirect(url_for('main.user', username = username))

#Функция отписки
@main.route('/unfollow/<username>')
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
	return redirect(url_for('main.user', username = username))

#ФУНКЦИЯ ПРОСМОТРА ФОЛЛОВЕРОВ
@main.route('/user/<username>/followers')
@login_required
def followers(username):
	user = User.query.filter_by(username = username).first()
	followers = user.followers
	return render_template('followers.html', followers = followers)

#ФУНКЦИЯ ПРОСМОТРА НА КОГО ПОДПИСАН
@main.route('/user/<username>/followed')
@login_required
def followed(username):
	user = User.query.filter_by(username = username).first()
	followeds = user.followed
	return render_template('followed.html', user = user, followeds = followeds)



