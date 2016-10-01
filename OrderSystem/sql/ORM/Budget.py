from OrderSystem import db


class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, nullable=False)
    subteam_id = db.Column(db.Integer, nullable=False, unique=False)
    dollar_amount = db.Column('dollar_amount', db.Numeric(15, 2), nullable=False)
    fiscal_year = db.Column('fiscal_year', db.Integer, nullable=False)

    def __init__(self, subteam_id, dollar_amount, fiscal_year):
        self.subteam_id = subteam_id
        self.dollar_amount = dollar_amount
        self.fiscal_year = fiscal_year
