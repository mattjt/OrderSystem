from OrderSystem import db


class Subteam(db.Model):
    __tablename__ = "subteams"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column('name', db.String(100), unique=True, nullable=False)
    hidden_from_choosable_subteams_list = db.Column(db.Boolean, nullable=False)

    def __init__(self, name, hidden_from_choosable_subteams_list):
        self.name = name
        self.hidden_from_choosable_subteams_list = hidden_from_choosable_subteams_list
