from ConfigParser import SafeConfigParser

from Crypto.Random.random import getrandbits
from Crypto.Util.number import long_to_bytes
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

from OrderSystem.Common import CONFIG_ROOT

# Load app configuration
parser = SafeConfigParser()
parser.read(CONFIG_ROOT + "mysql.ini")
# Instantiate entire application
app = Flask(__name__, static_url_path='/static')

# Configure database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{0}:{1}@{2}/{3}'.format(parser.get("mysql", "mysql_user"),
                                                                         parser.get("mysql", "mysql_password"),
                                                                         parser.get("mysql", "mysql_host"),
                                                                         parser.get("mysql", "mysql_database"))
# App settings
app.config["VERBOSE_OUTPUT"] = True
app.config["SECRET_KEY"] = long_to_bytes(getrandbits(32))

# Instantiate SQLAlchemy
db = SQLAlchemy(app)

# Start login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize application routes
from OrderSystem import RouteController

RouteController.init()
