from flask import render_template, redirect, url_for, Blueprint, abort
from flask_login import current_user, login_required

from OrderSystem import forms
from OrderSystem import login_manager, db
from OrderSystem.sql.ORM import User, Order, Vendor
from OrderSystem.utilities.Helpers import hash_password, flash_errors, needs_password_reset_check, get_fiscal_year
from OrderSystem.utilities.ServerLogger import log_event

main = Blueprint('main', __name__)


# Index
@main.route('/')
@login_required
@needs_password_reset_check
def index():
    fiscal_year = get_fiscal_year()

    orders_this_fiscal_year = db.session.query(Order).filter(Order.fiscal_year == fiscal_year)
    all_vendors = db.session.query(Vendor)

    # Some simple statistics
    num_of_orders_this_year = orders_this_fiscal_year.count()
    money_spent_this_season = 0
    for order in orders_this_fiscal_year:
        money_spent_this_season += order.total
    num_of_vendors = all_vendors.count()

    return render_template('index.html', page="dashboard", orders_this_year=num_of_orders_this_year,
                           money_spent_this_season=money_spent_this_season, num_of_vendors=num_of_vendors,
                           fiscal_year=fiscal_year)


# Force password reset
@main.route('/user/force-password-reset', methods=['GET', 'POST'])
@login_required
def force_password_reset():
    try:
        form = forms.ResetPassword()
        user = db.session.query(User).filter(User.id == current_user.id).first()

        if form.validate_on_submit():
            user.password = hash_password(form.password.data)
            user.needs_password_reset = False
            db.session.commit()
            return redirect(url_for('auth.logout'))
        else:
            flash_errors(form)
        return render_template('auth/password-reset.html', form=form)
    except Exception as e:
        log_event("ERROR", e)
        abort(500)


# Load User Manager
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))
