import base64
import os

from flask import render_template, request, redirect, url_for, flash, abort
from flask_classy import FlaskView, route
from flask_login import current_user

from CRUDBase import CRUDBase
from OrderSystem import db, sentry
from OrderSystem import forms
from OrderSystem.sql.ORM import User, Subteam, Budget, Settings
from OrderSystem.utilities.Helpers import hash_password, flash_errors, generate_random_password, strip_non_ascii
from OrderSystem.utilities.Mailer import mail_registration, mail_password_reset
from OrderSystem.utilities.Permissions import admin_access_required
from OrderSystem.utilities.ServerLogger import log_event


class Admin(FlaskView, CRUDBase):
    route_base = ""

    def create(self):
        pass

    @route('')
    @admin_access_required
    def index(self):
        return render_template('admin/index.html', page="admin")

    def update(self):
        pass

    def delete(self):
        pass

    @route('/set-fiscal-year', methods=['GET', 'POST'])
    @admin_access_required
    def set_fiscal_year(self):
        try:
            fiscal_setting = db.session.query(Settings).filter(Settings.key == "fiscal_year").first()

            if request.method == "POST":
                new_fiscal_year = int(request.values['newFiscalYear'])
                fiscal_setting.value = new_fiscal_year
                db.session.commit()
                return redirect(url_for('Admin:index'))
            return render_template('admin/fiscal-year.html', current_year=fiscal_setting.value, page="admin")
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)


class UserManager(FlaskView, CRUDBase):
    route_base = ""

    @route('/new', methods=['GET', 'POST'])
    @admin_access_required
    def create(self):
        """
        Add a new user
        """
        form = forms.CreateNewUser()
        subteams = db.session.query(Subteam).filter(Subteam.hidden_from_choosable_subteams_list == False)

        if form.validate_on_submit():
            try:
                username = strip_non_ascii(form.username.data)
                first_name = strip_non_ascii(form.first_name.data)
                last_name = strip_non_ascii(form.last_name.data)
                password = base64.urlsafe_b64encode(os.urandom(8))
                email = strip_non_ascii(form.email.data)
                is_admin = form.is_admin.data
                can_receive_pending_orders = form.can_receive_pending_orders.data
                can_approve_orders = form.can_approve_orders.data
                can_update_order_status = form.can_update_order_status.data
                can_receive_order_notifications = form.can_receive_order_notifications.data
                subteam = request.form['subteam']

                # Check if username is already taken
                username_exists = db.session.query(User).filter(User.username == username).first()

                if username_exists is not None:
                    flash("Username already taken!", 'error')
                    return render_template('admin/users/add-user.html', form=form, subteams=subteams, page="admin")

                # Check if email is already in use
                email_exists = db.session.query(User).filter(User.email == email).first()

                if email_exists is not None:
                    flash("Email exists!", 'error')
                    return render_template('admin/users/add-user.html', form=form, subteams=subteams, page="admin")

                # Create the user
                db.session.add(
                    User(username, first_name, last_name, hash_password(password), email,
                         is_admin,
                         can_receive_pending_orders,
                         can_approve_orders,
                         can_update_order_status,
                         can_receive_order_notifications,
                         subteam))
                db.session.commit()
                log_event('AUDIT', "{0} added new user [{1}]".format(current_user.username, username))

                # Send user email with temp password
                mail_registration(email, first_name, last_name, username, password)
                return redirect(url_for('UserManager:index'))
            except Exception as e:
                db.session.rollback()
                log_event("ERROR", e)
                sentry.captureException()
                flash("Unknown database error! [{0}]".format(e), 'error')
        else:
            flash_errors(form)
        return render_template('admin/users/add-user.html', form=form, subteams=subteams, page="admin")

    @route('')
    @admin_access_required
    def index(self):
        users = db.session.query(User)
        return render_template('admin/users/index.html', users=users, page="admin")

    # Edit user given user_id
    @route('/edit/<int:user_id>', methods=['GET', 'POST'])
    @admin_access_required
    def update(self, user_id):
        form = forms.CreateNewUser()
        error = None
        subteams = db.session.query(Subteam).filter(Subteam.hidden_from_choosable_subteams_list == False)

        if form.validate_on_submit():
            try:
                user_to_update = User.query.filter(User.id == user_id).first()

                # Gather information
                username = strip_non_ascii(form.username.data)
                first_name = strip_non_ascii(form.first_name.data)
                last_name = strip_non_ascii(form.last_name.data)
                email = strip_non_ascii(form.email.data)
                is_admin = form.is_admin.data
                can_receive_pending_orders = form.can_receive_pending_orders.data
                can_approve_orders = form.can_approve_orders.data
                can_update_order_status = form.can_update_order_status.data
                can_receive_order_notifications = form.can_receive_order_notifications.data
                subteam = request.form['subteam']

                # Update user object
                user_to_update.username = username
                user_to_update.first_name = first_name
                user_to_update.last_name = last_name
                user_to_update.email = email
                user_to_update.is_admin = is_admin
                user_to_update.can_receive_pending_orders = can_receive_pending_orders
                user_to_update.can_approve_orders = can_approve_orders
                user_to_update.can_update_order_status = can_update_order_status
                user_to_update.can_receive_order_notifications = can_receive_order_notifications
                user_to_update.subteam = subteam

                # Commit changes
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                log_event("ERROR", e)
                sentry.captureException()
                flash("Unknown database error! [{0}]".format(e), 'error')

            return redirect(url_for('UserManager:index'))

        else:
            flash_errors(form)

        user = db.session.query(User).filter(User.id == user_id).first()

        return render_template('admin/users/edit-user.html', user=user, form=form, error=error, subteams=subteams, page="admin")

    @route('/delete/<int:user_id>')
    @admin_access_required
    def delete(self, user_id):
        """
        Delete a user given user_id

        @param user_id:  Users ID
        @return: Redirect to admin dashboard
        """
        try:
            user_to_del = db.session.query(User).filter(User.id == user_id).first()

            if user_to_del is None:
                flash("ERROR! Cannot delete a user that doesn't exist!", 'error')
            else:
                if current_user.id == user_to_del.id:
                    flash("ERROR! You can't delete yourself!", 'error')
                else:
                    db.session.delete(user_to_del)
                    db.session.commit()
            return redirect(url_for('UserManager:index'))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)

    @route('/admin/users/reset-password/<int:user_id>')
    @admin_access_required
    def enable_forced_password_reset(self, user_id):
        """
        Email user a new password that is changed upon next login

        @param user_id: User ID
        @return: Redirect to user manager dashboard
        """
        try:
            user = db.session.query(User).filter(User.id == user_id).first()
            user.needs_password_reset = True
            password = generate_random_password()
            user.password = hash_password(password)
            mail_password_reset(user, password)
            db.session.commit()
            flash("Successfully reset users password!")
            return redirect(url_for('UserManager:index'))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)

    @route('/admin/users/disable-account/<int:user_id>')
    @admin_access_required
    def disable_account(self, user_id):
        """
        Disable a user's account by changing their password to a random 64-character string

        :param user_id: User ID
        :return: Redirect to admin dashboard
        """
        try:
            user = db.session.query(User).filter(User.id == user_id).first()
            password = generate_random_password(password_length=64)
            user.password = hash_password(password)
            user.username = str(user.username + "-DISABLED")
            db.session.commit()
            flash("Successfully disabled account!")
            return redirect(url_for('UserManager:index'))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)

    @route('/admin/users/enable-account/<int:user_id>')
    @admin_access_required
    def enable_account(self, user_id):
        """
        Re-enable the user's account by emailing them a new password

        :param user_id: User ID
        :return: Redirect to admin dashboard
        """
        try:
            user = db.session.query(User).filter(User.id == user_id).first()
            user.needs_password_reset = True
            password = generate_random_password()
            user.password = hash_password(password)
            user.username = str(user.username).replace("-DISABLED", "")
            mail_password_reset(user, password)
            db.session.commit()
            flash("Successfully enabled account!")
            return redirect(url_for('UserManager:index'))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)


class SubteamManager(FlaskView, CRUDBase):
    """
    Manages the subteams that are recognized in the ordering menu and the budgets display page
    """
    route_base = ""

    @route('/new', methods=['GET', 'POST'])
    @admin_access_required
    def create(self):
        """
        Add a new subteam
        @return: Add subteam page
        """
        form = forms.CreateSubteam()

        if form.validate_on_submit():
            try:
                db.session.add(
                    Subteam(strip_non_ascii(form.subteam_name.data), form.hidden_from_choosable_subteams_list.data))
                db.session.commit()
                log_event("AUDIT",
                          "{0} created a new subteam called {1}".format(current_user.username, form.subteam_name.data))
                return redirect(url_for('SubteamManager:index'))
            except Exception as e:
                db.session.rollback()
                log_event("ERROR", e)
                sentry.captureException()
                flash("Unknown database error!", 'error')
        else:
            flash_errors(form)
        return render_template('admin/subteams/add-subteam.html', form=form, page="admin")

    @route('')
    @admin_access_required
    def index(self):
        """
        List overview of all available subteams/order groups
        @return: Subteam manager dashboard
        """
        subteams = db.session.query(Subteam)
        return render_template('admin/subteams/index.html', subteams=subteams, page="admin")

    @route('/edit/<int:subteam_id>', methods=['GET', 'POST'])
    @admin_access_required
    def update(self, subteam_id):
        """
        Edit a subteam given subteam_id
        @param subteam_id: Subteam ID
        @return: Edit subteam page
        """
        form = forms.CreateSubteam()
        subteam = db.session.query(Subteam).filter(Subteam.id == subteam_id).first()

        if form.validate_on_submit():
            try:
                subteam.name = strip_non_ascii(form.subteam_name.data)
                subteam.hidden_from_choosable_subteams_list = form.hidden_from_choosable_subteams_list.data

                db.session.commit()
                return redirect(url_for('SubteamManager:index'))
            except Exception as e:
                db.session.rollback()
                log_event("ERROR", e)
                sentry.captureException()
                flash("Unknown database error!", 'error')
        else:
            flash_errors(form)
        return render_template('admin/subteams/edit-subteam.html', form=form, subteam=subteam, page="admin")

    @route('/delete/<int:subteam_id>')
    @admin_access_required
    def delete(self, subteam_id):
        """
        Delete a subteam given subteam_id
        @param subteam_id: Subteam ID
        @return: Redirect to subteam manager dashboard
        """
        try:
            try:
                db.session.delete(db.session.query(Budget).filter(Budget.subteam_id == subteam_id).first())
            except Exception as e:
                log_event("ERROR", e)
                flash("Budget wasn't set for subteam. Skipping budget deletion!")
            db.session.delete(db.session.query(Subteam).filter(Subteam.id == subteam_id).first())
            db.session.commit()
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            flash("You can't delete this subteam! There are team members that are still members of it!", 'warning')

        return redirect(url_for('SubteamManager:index'))
