from app import mail
from flask_mail import Message
from flask import render_template, current_app



def send_mail(subject, sender, recipients, text_body):
    msg = Message(subject = subject, sender = sender, recipients = recipients)
    msg.body = text_body
    mail.send(msg)


def send_reset_password_email(user):
    token = user.get_reset_password_token()
    send_mail('Сброс пароля Drinktime', current_app.config['ADMINS'][0], [user.email],
              text_body = render_template('reset_password.txt', user = user, token = token))

