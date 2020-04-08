from flask import render_template, flash, redirect, url_for
from app.authification import auth
from app.models import User
from flask_login import login_user, current_user, logout_user
from app.authification.forms import LoginForm, EmailToResetPassword,  ResetPasswordForm
from app.authification.email import send_reset_password_email
from app import db



@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username = form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            flash('Неправильное имя пользователя или пароля')
            return redirect(url_for('auth.login'))
        login_user(u)
        flash('Успешно')
        return redirect(url_for('main.index'))
    return render_template('login.html', form = form )


@auth.route('/logout', methods = ['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/reset_password_request', methods = ['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = EmailToResetPassword()
    if form.validate_on_submit():
        u = User.query.filter_by(email = form.email.data).first()
        if u is not None:
            send_reset_password_email(u)
            flash('Успешно отправлено, проверьте почту')
            return redirect(url_for('auth.login'))
        else:
            flash('Не найден пользователь с такой почтой')
    return render_template('reset_password_request.html', form = form)


@auth.route('/reset_password/<token>', methods = ['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    u = User.verify_reset_password_token(token)
    if u is None:
        return redirect(url_for('main.index'))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            u.set_password(form.password1.data)
            db.session.commit()
            flash('Вы успешно изменили пароль')
            return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form = form)