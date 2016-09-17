#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))
from datetime import date

from OrderSystem import db
from OrderSystem.sql.ORM import Settings, User, Subteam
from OrderSystem.utilities.Helpers import hash_password

print ("""
----------------------------------------------------------------------------------------------------------------
IF YOU ENCOUNTER MYSQL RELATED ERRORS WHILE RUNNING THIS SCRIPT, MAKE SURE THAT YOU HAVE CHANGED THE DEFAULT
SETTINGS FOR MYSQL IN /configuration/mysql.ini !!!
----------------------------------------------------------------------------------------------------------------
""")

# Empty DB
db.drop_all()

# Create all tables
db.create_all()

# Add default fiscal_year settings
db.session.add(Settings(key="fiscal_year", value=date.today().year))

db.session.add(Subteam("Order System Admin", False))
db.session.add(
    User("robotics-osa", "MORT", "Admin", hash_password('admin'), "delete_me@mort11.org", True, True, True, True, True,
         1))
db.session.commit()
print ("Done")
