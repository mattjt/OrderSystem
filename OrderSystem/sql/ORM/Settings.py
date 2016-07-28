from OrderSystem import db


class Settings(db.Model):
    __tablename__ = "settings"
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, nullable=False)
    key = db.Column('key', db.String(100), unique=True, nullable=False)
    value = db.Column('value', db.String(200), nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value
