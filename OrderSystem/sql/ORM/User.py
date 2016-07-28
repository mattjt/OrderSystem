from sqlalchemy.orm import backref

from OrderSystem import db
from OrderSystem.sql.ORM import Subteam


class User(db.Model):
    __tablename__ = "users"
    id = db.Column('id', db.Integer, primary_key=True)

    # Account Info
    username = db.Column('username', db.String(30), unique=True, nullable=False)
    first_name = db.Column('first_name', db.String(30), nullable=False)
    last_name = db.Column('last_name', db.String(30), nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    email = db.Column('email', db.String(50), unique=True, nullable=False)
    subteam = db.Column('subteam', db.Integer, db.ForeignKey('subteams.id'), nullable=False)
    subteam_ref = db.relationship(Subteam, backref=backref('user'))

    # Permissions
    is_admin = db.Column(db.Boolean, nullable=False)
    can_receive_pending_orders = db.Column(db.Boolean, nullable=False)
    can_approve_orders = db.Column(db.Boolean, nullable=False)
    can_update_order_status = db.Column(db.Boolean, nullable=False)
    can_receive_order_notifications = db.Column(db.Boolean, nullable=False)

    # Settings
    needs_password_reset = db.Column(db.Boolean, nullable=False)

    def __init__(self, username, first_name, last_name, password, email, is_admin, can_receive_pending_orders,
                 can_approve_orders, can_update_order_status, can_receive_order_notifications, subteam):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.email = email
        self.is_admin = is_admin
        self.can_receive_pending_orders = can_receive_pending_orders
        self.can_approve_orders = can_approve_orders
        self.can_update_order_status = can_update_order_status
        self.can_receive_order_notifications = can_receive_order_notifications
        self.subteam = subteam

        # New users need their password reset always
        self.needs_password_reset = False

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % self.username
