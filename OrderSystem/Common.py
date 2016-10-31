import os

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_ROOT = APP_ROOT + "/configuration/"
TEMPLATE_ROOT = APP_ROOT + "/OrderSystem/templates"
STATIC_ROOT = APP_ROOT + "/OrderSystem/static"
DEBUG_MODE = True
