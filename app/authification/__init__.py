from flask import Blueprint
from flask_login import LoginManager
from flask_babel import lazy_gettext as _l


auth = Blueprint('auth', __name__, template_folder = 'templates')



from app.authification import routes, forms