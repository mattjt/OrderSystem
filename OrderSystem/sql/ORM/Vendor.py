from OrderSystem import db


class Vendor(db.Model):
    __tablename__ = "vendors"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, nullable=False)
    vendor_name = db.Column('vendor_name', db.String(200), unique=True, nullable=False)
    vendor_url = db.Column('vendor_url', db.String(275), nullable=False)
    vendor_email = db.Column('vendor_email', db.String(125), nullable=True)
    vendor_phone = db.Column('vendor_phone', db.String(50), nullable=True)

    def __init__(self, name, url, email, phone):
        self.vendor_name = name
        self.vendor_url = url
        self.vendor_email = email
        self.vendor_phone = phone
