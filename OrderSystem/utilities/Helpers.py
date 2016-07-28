import base64
import os
import random
from functools import wraps

import scrypt
from flask import flash, url_for, redirect
from flask.ext.login import current_user

from OrderSystem import db
from OrderSystem.sql.ORM import User, Settings


def randstr(length):
    return ''.join(chr(random.randint(0, 255)) for i in range(length))


def hash_password((password), max_time=2.5, data_length=64):
    return scrypt.encrypt(randstr(data_length), str(password), maxtime=max_time)


def verify_password(hashed_password, guessed_password):
    try:
        scrypt.decrypt(hashed_password, str(guessed_password))
        return True
    except scrypt.error:
        return False


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0}".format(error), 'error')


def get_order_notification_recipients():
    """
    Gets all users with the can_receive_order_notifications permission

    @return: Array of all users with can_receive_order_notifications permission
    """

    all_users = db.session.query(User)
    mailing_list = []

    for user in all_users:
        if user.receive_site_mail:
            mailing_list.append(user.email)
    return mailing_list


def needs_password_reset_check(function):
    """
    Checks if the current user's session has the needs_password_reset flag set. If so, redirect them to the password
    reset page

    @param function: Function to wrap
    @return: Function to wrap or redirect to password reset page
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated() and current_user.needs_password_reset:
            return redirect(url_for('main.force_password_reset'))
        else:
            return function(*args, **kwargs)

    return wrapper


def generate_random_password():
    """
    Used to generate temporary passwords for new/password-reset accounts
    @return: 8 character base64 password
    """
    return base64.urlsafe_b64encode(os.urandom(8))


def get_fiscal_year():
    """
    @return: Current fiscal year
    """
    # Get current fiscal_year
    fiscal_year = db.session.query(Settings).filter(Settings.key == "fiscal_year").first()
    return fiscal_year.value
