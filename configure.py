from OrderSystem.sql.ORM import Settings
from OrderSystem import db

# Create all tables
db.create_all()

# Add default fiscal_year settings
db.session.add(Settings(key="fiscal_year", value=2016)).commit()
