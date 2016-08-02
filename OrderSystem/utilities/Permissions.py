from functools import wraps

from flask import abort, redirect, url_for, request
from flask_login import current_user


def get_path():
    return str(request.path).strip('/')


def admin_access_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.is_admin:
                return func(*args, **kwargs)
            else:
                abort(403)
        else:
            return redirect(url_for('auth.login') + "?prev={0}".format(get_path()))

    return wrapper


def update_order_status_access_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login') + "?prev={0}".format(get_path()))
        else:
            if current_user.can_update_order_status or current_user.is_admin:
                return func(*args, **kwargs)
            else:
                abort(403)

    return wrapper


def approve_order_access_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login') + "?prev={0}".format(get_path()))
        else:
            if current_user.can_approve_orders or current_user.is_admin:
                return func(*args, **kwargs)
            else:
                abort(403)

    return wrapper
