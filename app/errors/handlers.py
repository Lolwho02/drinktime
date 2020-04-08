from flask import render_template
from app.errors import errors



@errors.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
@errors.app_errorhandler(500)
def iternal_error(error):
    return render_template('500.html'), 500