from flask import render_template, request, redirect, url_for, flash
from flask.ext.classy import route, FlaskView
from flask.ext.login import login_required, current_user

from CRUDBase import CRUDBase
from OrderSystem import db
from OrderSystem import forms
from OrderSystem.sql.ORM import User
from OrderSystem.utilities.Helpers import verify_password, hash_password, flash_errors


class Users(FlaskView, CRUDBase):
    """
    The Users class handles managing a user's account settings
    """

    route_base = ""

    def create(self):
        pass

    @route('/profile', methods=['GET', 'POST'])
    @login_required
    def index(self):
        user = db.session.query(User).filter(User.id == current_user.id).first()

        return render_template('user/index.html', user=user)

    @route('/change-password', methods=['GET', 'POST'])
    @login_required
    def update(self):
        form = forms.ChangePassword(request.form)
        if form.validate_on_submit():
            if verify_password(current_user.passwd_hash, form.current_password.data):
                user = db.session.query(User).filter(User.id == current_user.id).first()
                user.passwd_hash = hash_password(form.new_password.data)
                db.session.commit()
                flash("Successfully changed password!")
                return redirect(url_for('auth.logout'))
            else:
                flash("Current password is incorrect!")
        else:
            flash_errors(form)
        return render_template('user/change-password.html', form=form)

    def delete(self):
        pass
