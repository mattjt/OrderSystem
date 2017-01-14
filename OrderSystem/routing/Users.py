from flask import render_template, request, redirect, url_for, flash
from flask_classy import FlaskView, route
from flask_login import login_required, current_user

from CRUDBase import CRUDBase
from OrderSystem import db
from OrderSystem import forms
from OrderSystem.sql.ORM import User
from OrderSystem.utilities.Helpers import verify_password, hash_password, flash_errors, strip_non_ascii


class Users(FlaskView, CRUDBase):
    """
    The Users class handles managing a user's account settings
    """

    route_base = ""

    def create(self):
        pass

    def index(self):
        pass

    @route('/change-password', methods=['GET', 'POST'])
    @login_required
    def update(self):
        form = forms.ChangePassword(request.form)
        if form.validate_on_submit():
            if verify_password(current_user.password, strip_non_ascii(form.current_password.data)):
                user = db.session.query(User).filter(User.id == current_user.id).first()
                user.password = hash_password(strip_non_ascii(form.new_password.data))
                db.session.commit()
                flash("Successfully changed password!", 'success')
                return redirect(url_for('auth.logout'))
            else:
                flash("Current password is incorrect!", 'error')
        else:
            flash_errors(form)
        return render_template('settings/users/change-password.html', form=form)

    def delete(self):
        pass
