#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))

from OrderSystem import db
from OrderSystem.sql.ORM import User
from OrderSystem.utilities.Helpers import hash_password

"""
Script for resetting passwords of individual users from the command line
"""

username_to_reset = raw_input("Enter username to reset: ")
new_password = raw_input("Enter new password: ")

user = db.session.query(User).filter(User.username == username_to_reset).first()
if user is not None:
    user.password = hash_password(new_password)
    db.session.commit()
    print ("Password has been reset")
else:
    print("Specified user does not exist! Terminating...")
