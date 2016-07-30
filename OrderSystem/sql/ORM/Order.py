from OrderSystem import db


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, nullable=False)
    fiscal_year = db.Column('fiscal_year', db.Integer, nullable=False)

    # Vendor Info
    vendor_id = db.Column('vendor_id', db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    vendor = db.relationship('Vendor', foreign_keys=[vendor_id])

    # Part Info
    part_name = db.Column('part_name', db.String(150), nullable=False)
    part_url = db.Column('part_url', db.String(350), nullable=False)
    part_number = db.Column('part_number', db.String(15), nullable=False)
    part_quantity = db.Column('part_quantity', db.Integer, nullable=False)
    part_unit_price = db.Column('part_unit_price', db.Numeric(15, 2), nullable=False)
    part_total_price = db.Column('part_total_price', db.Numeric(15, 2), nullable=False)
    part_shipping_cost = db.Column('part_shipping_cost', db.Numeric(15, 2), nullable=False, default=0)
    credit = db.Column('part_credit', db.Numeric(15, 2), nullable=False, default=0)

    # MetaData
    part_needed_by = db.Column('part_needed_by', db.String(150), nullable=False)
    part_for_subteam = db.Column('part_for_subteam', db.ForeignKey('subteams.id'), nullable=False)
    subteam = db.relationship('Subteam', foreign_keys=[part_for_subteam])
    part_ordered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ordering_user = db.relationship('User', foreign_keys=[part_ordered_by])
    part_ordered_on = db.Column('part_ordered_on', db.String(150), nullable=False)
    total = db.Column('total', db.Numeric(15, 2), nullable=False)
    order_status = db.Column('order_status', db.String(150), nullable=False)

    # Advisor input
    pending_approval = db.Column('pending_approval', db.Boolean, nullable=False)
    order_dirty = db.Column('order_dirty', db.Boolean, nullable=False)

    def __init__(self, fiscal_year, vendor_id, part_name, part_url, part_number, part_quantity, part_unit_price,
                 part_total_price, part_needed_by, part_for_subteam, part_ordered_by, part_ordered_on, total):
        self.fiscal_year = fiscal_year
        self.part_name = part_name
        self.vendor_id = vendor_id
        self.part_url = part_url
        self.part_number = part_number
        self.part_quantity = part_quantity
        self.part_unit_price = part_unit_price
        self.part_total_price = part_total_price
        self.part_needed_by = part_needed_by
        self.part_for_subteam = part_for_subteam
        self.part_ordered_by = part_ordered_by
        self.part_ordered_on = part_ordered_on
        self.total = total
        self.order_status = "unprocessed"
        self.pending_approval = True
        self.order_dirty = True
