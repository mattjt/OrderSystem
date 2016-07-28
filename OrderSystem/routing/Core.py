import os

from flask import render_template, redirect, url_for, Blueprint, abort, send_from_directory
from flask.ext.login import current_user, login_required

from OrderSystem import forms
from OrderSystem import login_manager, db
from OrderSystem.sql.ORM import User
from OrderSystem.utilities.Helpers import hash_password, flash_errors, needs_password_reset_check

main = Blueprint('main', __name__)


# Index
@main.route('/')
@needs_password_reset_check
def index():
    return render_template('index.html', page="dashboard")


# Force password reset
@main.route('/user/force-passwd-reset', methods=['GET', 'POST'])
@login_required
def force_password_reset():
    form = forms.ResetPasswd()
    error = None
    user = db.session.query(User).filter(User.id == current_user.id).first()

    if form.validate_on_submit():
        passwd_raw = form.password.data
        new_password = hash_password(passwd_raw)

        user.password = new_password
        user.needs_passwd_reset = False
        db.session.commit()
        return redirect(url_for('auth.logout'))
    else:
        flash_errors(form)
    return render_template('auth/force-passwd-reset.html', form=form, error=error)


# Wildcard page loader
@main.route('/<path:page_url>')
@needs_password_reset_check
def page_loader(page_url):
    try:
        return render_template("render-files/page/{0}.html".format(page_url))
    except:
        abort(404)


@main.route('/robots.txt')
def robots_txt():
    return send_from_directory('{0}/OrderSystem/static'.format(os.environ.get('APPLICATION_ROOT')), 'robots.txt')


# Load UserManagement
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))
