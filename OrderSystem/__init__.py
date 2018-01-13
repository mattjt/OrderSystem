***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

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
sentry = Sentry(app, dsn='https://f8ef7f188bf94deb898536d0668c4a29:5e30affaa5984a429a8af228a8baeed4@sentry.io/271212')

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
