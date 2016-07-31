#!/usr/bin/env python
import os

CONFIG_ROOT = os.path.dirname(os.getcwd()) + "/configuration/"
LOG_ROOT = os.path.dirname(os.getcwd()) + "/logs/"

# Create config dir if not exist
if not os.path.isdir(CONFIG_ROOT):
    os.mkdir(CONFIG_ROOT)

# Create core.ini
if not os.path.isfile(CONFIG_ROOT + "core.ini"):
    # Boilerplate config
    f_contents = "[core]\nverbose_output=False"
    with open(CONFIG_ROOT + "core.ini", 'w') as core:
        core.write(f_contents)

# Create mailgun.ini
if not os.path.isfile(CONFIG_ROOT + "mailgun.ini"):
    # Boilerplate config
    f_contents = "[mailgun]\napi_url = YOUR_API_URL\napi_key = YOUR_API_KEY"
    with open(CONFIG_ROOT + "mailgun.ini", 'w') as mailgun:
        mailgun.write(f_contents)

# Create mysql.ini
if not os.path.isfile(CONFIG_ROOT + "mysql.ini"):
    # Boilerplate config
    f_contents = "[mysql]\nmysql_user = YOUR_MYSQL_USER\nmysql_password = YOUR_MYSQL_PASSWORD\nmysql_database = YOUR_MYSQL_DATABASE\nmysql_host = YOUR_MYSQL_HOST"
    with open(CONFIG_ROOT + "mysql.ini", 'w') as mysql:
        mysql.write(f_contents)

# Create logs dir if not exist
if not os.path.isdir(LOG_ROOT):
    os.mkdir(LOG_ROOT)
