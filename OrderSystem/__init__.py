from ConfigParser import SafeConfigParser

from Crypto.Random.random import getrandbits
from Crypto.Util.number import long_to_bytes
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from OrderSystem.Common import CONFIG_ROOT

# Load app configuration
mysql_conf_parser = SafeConfigParser()
mysql_conf_parser.read(CONFIG_ROOT + "mysql.ini")

# Instantiate entire application
app = Flask(__name__, static_url_path='/static')

# Configure database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{0}:{1}@{2}/{3}'.format(mysql_conf_parser.get("mysql", "mysql_user"),
                                                                         mysql_conf_parser.get("mysql",
                                                                                               "mysql_password"),
                                                                         mysql_conf_parser.get("mysql", "mysql_host"),
                                                                         mysql_conf_parser.get("mysql",
                                                                                               "mysql_database"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# App settings
app.config["VERBOSE_OUTPUT"] = True
app.config["SECRET_KEY"] = long_to_bytes(getrandbits(32))

# Instantiate SQLAlchemy
db = SQLAlchemy(app)

# Setup sentry logging
sentry_conf_parser = SafeConfigParser()
sentry_conf_parser.read(CONFIG_ROOT + "sentry.ini")
sentry = Sentry(app, dsn=sentry_conf_parser.get("sentry", "dsn"))

# Start login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize application routes
from OrderSystem import RouteController

RouteController.init()
