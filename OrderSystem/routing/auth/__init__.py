from flask import redirect, url_for, request, render_template, Blueprint, flash
from flask_login import login_user, logout_user
from sqlalchemy import or_

from OrderSystem import forms, db, app
from OrderSystem.sql.ORM import User, Subteam
from OrderSystem.utilities.Helpers import verify_password, flash_errors, hash_password
from OrderSystem.utilities.ServerLogger import log_event

auth = Blueprint('auth', __name__)


# Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.Login()

    if form.validate_on_submit():
        username = form.username.data.strip(" ").lower()
        guessed_password = form.password.data.strip(" ")

        # Find matching user
        user = db.session.query(User).filter(or_(User.username == username, User.email == username)).first()

        # Guest tried to login as non-existent user
        if user is None:
            log_event('INFO', 'Guest tried to login as non-existent user.')
            flash("Invalid username/password!")
            return render_template('auth/login.html', form=form)

        # Check if passwords match
        if verify_password(user.passwd_hash, guessed_password):
            login_user(user, remember=True)

            # Redirect to previous page
            return redirect(request.args.get('prev') or request.args.get('next') or "/")

        # User/password pair is wrong
        else:
            flash("Incorrect username/password")
            log_event('WARNING', 'Guest incorrectly attempted to login as {0}.'.format(user.username))
            return render_template('auth/login.html', form=form)
    else:
        flash_errors(form)

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.SelfRegisterForm()
    subteams = db.session.query(Subteam).filter(Subteam.hidden_from_choosable_subteams_list == False)

    if form.validate_on_submit():
        if form.registration_code.data == app.config["REGISTRATION_CODE"]:
            try:
                username = form.username.data.strip(" ").lower()
                first_name = form.first_name.data
                last_name = form.last_name.data
                raw_passwd = form.password.data.strip(" ")
                email = form.email.data
                grad_year = form.grad_year.data
                team_role = form.team_role.data
                subteam = request.form['subteam']

                username_exists = db.session.query(User).filter(User.username == username).first()

                # Check if username is already taken
                if username_exists is not None:
                    flash("Username already taken!")
                    return render_template('auth/register.html', form=form, subteams=subteams)

                email_exists = db.session.query(User).filter(User.email == email).first()

                # Check if email is already in use
                if email_exists is not None:
                    flash("Email exists!")
                    return render_template('auth/register.html', form=form, subteams=subteams)

                    # Register them
                db.session.add(
                    User(username, first_name, last_name, hash_password(raw_passwd), email, grad_year, False, False,
                         False, True, False, False, False, True, False, subteam, team_role, False))

                db.session.commit()
                log_event('AUDIT',
                          "New account registered as \"{0}\" using registration code: {1}".format(username, app.config[
                              "REGISTRATION_CODE"]))
                their_subteam = db.session.query(Subteam).filter(Subteam.id == subteam).first()
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash("Unknown database error. If the error persists, please email mort11org@mort11.org {0}".format(e))
        else:
            flash("Incorrect registration code!")
            return render_template('auth/register.html', form=form, subteams=subteams)
    else:
        flash_errors(form)

    return render_template('auth/register.html', form=form, subteams=subteams)


# Logout
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
