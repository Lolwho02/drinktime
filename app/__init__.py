from flask import Flask, request, current_app  # импортирую из фласка главный класс - Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
import logging
from logging.handlers import SMTPHandler
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel, lazy_gettext as _l
from config import Config

login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Войдите в свой аккаунт для просмотра данной страницы')

db = SQLAlchemy()
migrate = Migrate()

mail = Mail()

bootstrap = Bootstrap()

moment = Moment()

babel = Babel()


def create_app(class_config = Config):
    app = Flask(__name__)
    app.config.from_object(class_config)
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    from app.errors import errors
    app.register_blueprint(errors)
    from app.authification import auth
    app.register_blueprint(auth, url_prefix='/auth')
    from app.main import main
    app.register_blueprint(main)
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
    return app



@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGE'])



from app import models
