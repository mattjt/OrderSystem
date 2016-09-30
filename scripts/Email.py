***REMOVED***

import jinja2
import requests
from jinja2 import Environment

from OrderSystem import Common

__author__ = "Matt Turi"
__copyright__ = "Copyright 2016, Mount Olive Robotics Team"
__license__ = "MIT"
__version__ = "0.4"
__maintainer__ = "Matt Turi"
__email__ = "mturi@mort11.org"
__status__ = "Production"

parser = SafeConfigParser()
parser.read(Common.CONFIG_ROOT + "mailgun.ini")


class Email(object):
    """
    Base class for sending emails
    """

    environment = Environment(loader=jinja2.FileSystemLoader(Common.TEMPLATE_ROOT))

    def __init__(self, subject, sender, to_address=None):
        self.subject = subject
        self.sender = sender
        self.html = ""
        self.to_address = to_address or []

    def get_environment(self):
        return self.environment

    def set_html(self, html):
        self.html = html

    def send(self):
        requests.post(
            parser.get("mailgun", "api_url"),
            auth=("api", parser.get("mailgun", "api_key")),
            data={"from": self.sender,
                  "to": self.to_address,
                  "subject": self.subject,
                  "text": self.html,
                  "html": self.html})
