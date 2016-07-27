import base64
import os

from flask import render_template, request, redirect, url_for, send_from_directory, Blueprint, flash
from flask.ext.classy import FlaskView, route
from flask.ext.login import current_user

from CRUDBase import CRUDBase
from OrderSystem import db
from OrderSystem import forms
from OrderSystem.sql.ORM import User, Subteam, Budget
from OrderSystem.utilities.Helpers import hash_password, flash_errors, generate_random_password
from OrderSystem.utilities.Mailer import mail_registration, mail_forced_password_reset, mail_forgotten_password_reset
from OrderSystem.utilities.Permissions import admin_access_required
from OrderSystem.utilities.ServerLogger import log_event

admin = Blueprint('admin', __name__)


class Admin(FlaskView, CRUDBase):
    route_base = ""

    def create(self):
        pass

    @route('/')
    @admin_access_required
    def index(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


class AdminManageUser(FlaskView, CRUDBase):
    route_base = ""

    @route('/users/new', methods=['GET', 'POST'])
    @admin_access_required
    def create(self):
        """
        Add a new user
        """
        form = forms.Register()
        subteams = db.session.query(Subteam).filter(Subteam.hidden_from_choosable_subteams_list == False)

        if form.validate_on_submit():
            try:
                username = form.username.data
                first_name = form.first_name.data
                last_name = form.last_name.data
                raw_passwd = base64.urlsafe_b64encode(os.urandom(8))
                email = form.email.data
                is_admin = form.is_admin.data
                can_view_orders = form.can_view_orders.data
                can_edit_orders = form.can_edit_orders.data
                can_approve_orders = form.can_approve_orders.data
                receive_site_mail = form.receive_site_mail.data
                can_update_order_status = form.can_update_order_status.data
                subteam = request.form['subteam']

                username_exists = db.session.query(User).filter(User.username == username).first()

                # Check if username is already taken
                if username_exists is not None:
                    flash("Username already taken!")
                    return render_template('admin/users/add-user.html', form=form, subteams=subteams)

                email_exists = db.session.query(User).filter(User.email == email).first()

                # Check if email is already in use
                if email_exists is not None:
                    flash("Email exists!")
                    return render_template('admin/users/add-user.html', form=form, subteams=subteams)

                    # Register them
                db.session.add(
                    User(username, first_name, last_name, hash_password(raw_passwd), email, is_admin,
                         can_view_orders, can_edit_orders, can_approve_orders, receive_site_mail,
                         can_update_order_status, subteam, True))

                db.session.commit()
                log_event('AUDIT', "{0} registered user {1}".format(current_user.username, username))

                # Send user email with temp password
                mail_registration(email, first_name, last_name, username, raw_passwd)

                their_subteam = db.session.query(Subteam).filter(Subteam.id == subteam).first()
                return redirect(url_for('admin.users_overview'))
            except Exception as e:
                db.session.rollback()
                flash("Unkown database error! [{0}]".format(e))
        else:
            flash_errors(form)
        return render_template('admin/users/add-user.html', form=form, subteams=subteams)

    @route('/users')
    @admin_access_required
    def index(self):
        users = db.session.query(User)
        return render_template('admin/users/index.html', users=users)

    def update(self):
        pass

    @route('/admin/users/delete/<int:user_id>')
    @admin_access_required
    def delete(self, user_id):
        """
        Delete a user given user_id
        @param user_id:  Users ID
        @return: Redirect to admin dashboard
        """
        user_to_del = db.session.query(User).filter(User.id == user_id).first()
        db.session.delete(user_to_del)
        db.session.commit()
        return redirect(url_for('admin.users_overview'))


# Reset user's password and email them a temporary one that needs reset upon login
@admin.route('/forgot-password', methods=['GET', 'POST'])
def forgotten_password():
    form = forms.ForgottenPassword(request.form)
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()

        if user is None:
            flash("Invalid email")
            return redirect(url_for("admin.forgotten_password"))

        temp_pass = generate_random_password()
        user.passwd_hash = hash_password(temp_pass)
        user.needs_passwd_reset = True
        db.session.commit()

        mail_forgotten_password_reset(form.email.data, user.username, temp_pass)
        return redirect(url_for("main.index"))
    else:
        flash_errors(form)
    return render_template('auth/forgot-password.html', form=form)


# Email user a new password that is changed upon next login
@admin.route('/admin/users/reset-password/<int:user_id>')
@admin_access_required
def enable_forced_password_reset(user_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    user.needs_passwd_reset = True
    password = generate_random_password()
    user.passwd_hash = hash_password(password)
    mail_forced_password_reset(user, password)
    db.session.commit()
    return redirect(url_for('admin.users_overview'))


# Delete a user given user_id
@admin.route('/admin/users/delete/<int:user_id>')
@admin_access_required
def delete_user(user_id):
    user_to_del = db.session.query(User).filter(User.id == user_id).first()
    db.session.delete(user_to_del)
    db.session.commit()
    return redirect(url_for('admin.users_overview'))


def add_user():
    pass


# Edit user given user_id
@admin.route('/admin/users/edit/<user_id>', methods=['GET', 'POST'])
@admin_access_required
def edit_user(user_id):
    form = forms.Register()
    error = None
    subteams = db.session.query(Subteam).filter(Subteam.hidden_from_choosable_subteams_list == False)
    team_roles = forms.team_positions

    if form.validate_on_submit():
        try:
            user_to_update = User.query.filter(User.id == user_id).first()

            username = form.username.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            grad_year = form.grad_year.data
            is_admin = form.is_admin.data
            can_use_cms = form.can_use_cms.data
            is_cms_admin = form.is_cms_admin.data
            can_view_orders = form.can_view_orders.data
            can_edit_orders = form.can_edit_orders.data
            can_approve_orders = form.can_approve_orders.data
            receive_site_mail = form.receive_site_mail.data
            can_update_order_status = form.can_update_order_status.data
            subteam = request.form['subteam']
            team_role = request.form['team_role']

            user_to_update.username = username
            user_to_update.first_name = first_name
            user_to_update.last_name = last_name
            user_to_update.email = email
            user_to_update.grad_year = grad_year
            user_to_update.is_admin = is_admin
            user_to_update.can_use_cms = can_use_cms
            user_to_update.is_cms_admin = is_cms_admin
            user_to_update.can_view_orders = can_view_orders
            user_to_update.can_edit_orders = can_edit_orders
            user_to_update.can_approve_orders = can_approve_orders
            user_to_update.receive_site_mail = receive_site_mail
            user_to_update.subteam = subteam
            user_to_update.team_role = team_role
            user_to_update.can_update_order_status = can_update_order_status

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Unknown database error! [{0}]".format(e))

        return redirect(url_for('admin.users_overview'))

    else:
        flash_errors(form)

    user = db.session.query(User).filter(User.id == user_id).first()

    return render_template('admin/users/edit-user.html', user=user, form=form, error=error, subteams=subteams,
                           team_roles=team_roles)


# List overview of all available subteams/order groups
@admin.route('/admin/subteams')
@admin_access_required
def subteam_manager_overview():
    subteams = db.session.query(Subteam)
    return render_template('admin/subteams/index.html', subteams=subteams)


# Add a new subteam
@admin.route('/admin/subteams/new', methods=['GET', 'POST'])
@admin_access_required
def add_subteam():
    form = forms.NewSubteam()
    if form.validate_on_submit():
        try:
            db.session.add(Subteam(form.subteam_name.data, form.subteam_description.data, form.hide_from_subteams.data,
                                   form.hide_from_budgets.data))
            db.session.commit()
            log_event("AUDIT",
                      "{0} created a new subteam called {1}".format(current_user.username, form.subteam_name.data))
            return redirect(url_for('admin.subteam_manager_overview'))
        except:
            db.session.rollback()
            flash("Unknown database error!")
    else:
        flash_errors(form)
    return render_template('admin/subteams/add-subteam.html', form=form)


# Edit a subteam given subteam_id
@admin.route('/admin/subteams/edit/<int:subteam_id>', methods=['GET', 'POST'])
@admin_access_required
def edit_subteam(subteam_id):
    form = forms.NewSubteam()
    subteam = db.session.query(Subteam).filter(Subteam.id == subteam_id).first()

    if form.validate_on_submit():
        try:
            subteam.name = form.subteam_name.data
            subteam.description = request.values['subteam_description']
            subteam.hidden_from_budgets_list = form.hide_from_budgets.data
            subteam.hidden_from_subteams_list = form.hide_from_subteams.data

            db.session.commit()
            return redirect(url_for('admin.subteam_manager_overview'))
        except:
            db.session.rollback()
            flash("Unknown database error!")
    else:
        flash_errors(form)
    return render_template('admin/subteams/edit-subteam.html', form=form, subteam=subteam)


# Delete a subteam given subteam_id
@admin.route('/admin/subteams/delete/<int:subteam_id>')
@admin_access_required
def delete_subteam(subteam_id):
    try:
        db.session.delete(db.session.query(Budget).filter(Budget.subteam_id == subteam_id).first())
        db.session.delete(db.session.query(Subteam).filter(Subteam.id == subteam_id).first())
        db.session.commit()

    except:
        flash("You can't delete this subteam! There are team members that are still members of it!")

    return redirect(url_for('admin.subteam_manager_overview'))


# Download a copy of the current log file
@admin.route('/admin/download-log')
@admin_access_required
def download_log():
    return send_from_directory('{0}/logs'.format(os.environ.get('APPLICATION_ROOT')), 'server.log')
