from flask_mail import Message
from app import app
from app import mail
from flask import render_template


def send_mail(subject, sender, recipients, text_body):
    message = Message(subject, sender = sender, recipients = recipients)
    message.body = text_body
    mail.send(message)


def send_reset_password_email(user):
    token = user.get_reset_password_token()
    send_mail('Восстановление доступа к сайту Drinktime', sender = app.config['ADMINS'][0], recipients = [user.email],
              text_body = render_template('email/reset_password.txt', user = user, token = token))