***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

***REMOVED***

***REMOVED***Bkp
parser = SafeConfigParser()
parser.read(CONFIG_ROOT + "mysql.ini")

***REMOVED***
***REMOVED***

***REMOVED***
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{0}:{1}@{2}/{3}'.format(parser.get("mysql", "mysql_user"),
                                                                         parser.get("mysql", "mysql_password"),
                                                                         parser.get("mysql", "mysql_host"),
                                                                         parser.get("mysql", "mysql_database"))
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
