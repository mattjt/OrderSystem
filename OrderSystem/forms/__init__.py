from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, IntegerField

from wtforms.fields.html5 import EmailField, DecimalField

from wtforms.validators import Email, URL, InputRequired, EqualTo


class Login(Form):
    username = StringField('Username/Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class ResetPassword(Form):
    password = PasswordField('New Password',
                             validators=[InputRequired(), EqualTo('confirm', message="Passwords must match!")])
    confirm = PasswordField('Repeat Password', validators=[InputRequired(message="Password confirmation required!")])


class CreateNewUser(Form):
    username = StringField('Username', validators=[InputRequired("Username is required!")])
    first_name = StringField('First Name', validators=[InputRequired("First name is required!")])
    last_name = StringField('Last Name', validators=[InputRequired("Last name is required!")])
    email = EmailField('Email', validators=[InputRequired("Email is required"), Email("Email is required!")])
    is_admin = BooleanField('Is Admin')
    can_receive_pending_orders = BooleanField('Can receive pending orders')
    can_approve_orders = BooleanField('Can approve/deny orders')
    can_update_order_status = BooleanField('Can update order status')
    can_receive_order_notifications = BooleanField('Can receive order notifications')


class NewVendor(Form):
    vendor_name = StringField('Vendor Name', validators=[InputRequired("Vendor name is required!")])
    vendor_url = StringField('Vendor URL', validators=[InputRequired("Vendor URL is required!"),
                                                       URL("Vendor URL is invalid!")])
    vendor_phone = StringField('Vendor Phone [Leave blank for none]')
    vendor_email = EmailField('Vendor Email [Leave blank for none]')


class CreateSubteam(Form):
    subteam_name = StringField('Subteam Name', validators=[InputRequired(message="Subteam name is required!")])
    hidden_from_choosable_subteams_list = BooleanField('Hidden from choosable subteams list')


class SetBudgetForm(Form):
    amount = IntegerField('Dollar Amount', validators=[InputRequired('Dollar amount is required!')])


class Order(Form):
    part_name = StringField('Part Name', validators=[InputRequired("Part name is required!")])
    part_url = StringField('Part URL', validators=[InputRequired("Part URL is required!"), URL("Part URL is invalid!")])
    part_number = StringField('Part Number')
    part_quantity = DecimalField('Part Quantity', validators=[InputRequired("Part quantity is required!")])
    part_unit_price = DecimalField('Part Unit Price', validators=[InputRequired("Part unit price is required!")])
    needed_by = StringField('Needed by', validators=[InputRequired("Needed by is required!")])


class ChangePassword(Form):
    current_password = PasswordField('Current Password', validators=[InputRequired("Current password is required!")])
    new_password = PasswordField('New Password',
                                 validators=[InputRequired("New password is required"),
                                             EqualTo('confirm', message="Passwords must match!")])
    confirm = PasswordField('Repeat New Password',
                            validators=[InputRequired(message="Password confirmation required!")])
