import os
from time import strftime

from OrderSystem import app


def log_event(log_level, msg):
    if log_level == "ERROR":
        logfile = open('{0}/logs/error.log'.format(os.environ.get('APPLICATION_ROOT')), "a")
        logfile.write("[{0}][{1}] >> {2}\n".format(get_time(), log_level, msg))
        logfile.close()
    else:
        logfile = open('{0}/logs/server.log'.format(os.environ.get('APPLICATION_ROOT')), "a")
        logfile.write("[{0}][{1}] >> {2}\n".format(get_time(), log_level, msg))
        logfile.close()


def console_print(log_level, msg, always_show=True):
    if app.config["VERBOSE_OUTPUT"]:
        print("[{0}][{1}] >> {2}".format(get_time(), log_level, msg))
    elif not app.config["VERBOSE_OUTPUT"] and always_show:
        print("[{0}][{1}] >> {2}".format(get_time(), log_level, msg))


def get_time():
    return strftime("%m-%d-%Y at %I:%M:%S%p")
