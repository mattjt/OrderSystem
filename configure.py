from OrderSystem import db
from OrderSystem.sql.ORM import Settings, User, Subteam
from OrderSystem.utilities.Helpers import hash_password

# Empty DB
db.drop_all()

# Create all tables
db.create_all()

# Add default fiscal_year settings
db.session.add(Settings(key="fiscal_year", value=2016))

db.session.add(Subteam("Programming", False))
db.session.add(
    User("admin", "MORT", "Admin", hash_password('admin'), "mort11or@mort11.org", True, True, True, True, True, 1))
db.session.commit()
