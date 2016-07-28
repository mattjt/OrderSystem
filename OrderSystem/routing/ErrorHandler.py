from flask import request, render_template
from flask.ext.login import current_user

from OrderSystem import app
from OrderSystem.utilities.ServerLogger import log_event


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def error_handler(error_code):
    if request.path == '/favicon.ico':
        # This is getting annoying
        pass
    else:
        log_event('ERROR', '{0} encountered {1} at {2}'.format(get_current_user(), error_code, request.path))
    return render_template('errors/base.html', error_code=error_code)


def get_current_user():
    if current_user.is_authenticated():
        return current_user.username
    else:
        return "Guest"


def init():
    pass