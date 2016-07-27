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
    passwd_hash = db.Column(db.LargeBinary, nullable=False)
    email = db.Column('email', db.String(50), unique=True, nullable=False)
    subteam = db.Column('subteam', db.Integer, db.ForeignKey('subteams.id'), nullable=False)
    subteam_ref = db.relationship(Subteam, backref=backref('user'))
    team_role = db.Column('team_role', db.String(50), nullable=False)

    # Permissions
    is_admin = db.Column(db.Boolean, nullable=False)
    can_approve_orders = db.Column(db.Boolean, nullable=False)
    receive_order_notifications = db.Column(db.Boolean, nullable=False)
    can_update_order_status = db.Column(db.Boolean, nullable=False)

    # Settings
    needs_passwd_reset = db.Column(db.Boolean, nullable=False)

    def __init__(self, username, first_name, last_name, passwd_hash, email, is_admin,
                 can_view_orders, can_edit_orders, can_approve_orders, receive_order_notifications,
                 can_update_order_status, subteam):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.passwd_hash = passwd_hash
        self.email = email
        self.is_admin = is_admin
        self.can_view_orders = can_view_orders
        self.can_edit_orders = can_edit_orders
        self.can_approve_orders = can_approve_orders
        self.receive_order_notifications = receive_order_notifications
        self.can_update_order_status = can_update_order_status
        self.subteam = subteam

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
