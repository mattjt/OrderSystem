from flask import redirect, url_for, request, render_template, Blueprint, flash
from flask_login import login_user, logout_user
from sqlalchemy import or_

from OrderSystem import forms, db
from OrderSystem.sql.ORM import User
from OrderSystem.utilities.Helpers import verify_password, flash_errors
from OrderSystem.utilities.ServerLogger import log_event

auth = Blueprint('auth', __name__)


# Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.Login()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Find matching user
        user = db.session.query(User).filter(or_(User.username == username)).first()

        # Guest tried to login as non-existent user
        if user is None:
            log_event('INFO', 'Guest tried to login as non-existent user.')
            flash("Invalid username/password!", 'error')
            return render_template('auth/login.html', form=form)

        # Check if passwords match
        if verify_password(user.password, password):
            login_user(user, remember=True)

            # Redirect to previous page
            return redirect(request.args.get('prev') or request.args.get('next') or "/")

        # User/password pair is wrong
        else:
            flash("Incorrect username/password", 'error')
            log_event('WARNING', 'Guest incorrectly attempted to login as {0}.'.format(user.username))
            return render_template('auth/login.html', form=form)
    else:
        flash_errors(form)

    return render_template('auth/login.html', form=form)


# Logout
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
