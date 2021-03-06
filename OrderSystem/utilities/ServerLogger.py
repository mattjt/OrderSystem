import os
from ConfigParser import SafeConfigParser
from time import strftime

from OrderSystem import Common

parser = SafeConfigParser()
parser.read(Common.CONFIG_ROOT + "core.ini")


def log_event(log_level, msg):
    # Create logs folder if it doesn't exist
    if not os.path.isdir(Common.APP_ROOT + "/logs"):
        os.mkdir(Common.APP_ROOT + "/logs")

    if log_level == "ERROR":
        logfile = open('{0}/logs/error.log'.format(Common.APP_ROOT), "a")
        logfile.write("[{0}][{1}] >> {2}\n".format(get_time(), log_level, msg))
        logfile.close()
    else:
        logfile = open('{0}/logs/server.log'.format(Common.APP_ROOT), "a")
        logfile.write("[{0}][{1}] >> {2}\n".format(get_time(), log_level, msg))
        logfile.close()


def console_print(log_level, msg, always_show=True):
    if parser.get("core", "verbose_output"):
        print("[{0}][{1}] >> {2}".format(get_time(), log_level, msg))
    elif not parser.get("core", "verbose_output") and always_show:
        print("[{0}][{1}] >> {2}".format(get_time(), log_level, msg))


def get_time():
    return strftime("%m-%d-%Y at %I:%M:%S%p")
