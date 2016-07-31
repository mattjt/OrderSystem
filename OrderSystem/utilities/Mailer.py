import requests
from flask import render_template

from OrderSystem.utilities.ServerLogger import log_event

DEFAULT_EMAIL = "no-reply@mort11.org"
DEFAULT_NAME = "MORT Orders"


#####################
# Mailing Framework #
#####################
def send_email(subject, recipients, body, sender_name=DEFAULT_NAME, sender_email=DEFAULT_EMAIL):
    try:
        requests.post(
            "https://api.mailgun.net/v3/mg.mort11.org/messages",
            auth=("api", "key-43bd883a0e65f3738340c81a0066a99a"),
            data={"from": "{0} <{1}>".format(sender_name, sender_email),
                  "to": recipients,
                  "subject": subject,
                  "text": subject,
                  "html": body})

        log_event("INFO", "Mailing Subsystem: Message(s) sent successfully!")

    except Exception, e:
        log_event("ERROR",
                  "Mailing subsystem encountered error!\n\n {0} \n -----------------------------------------".format(e))


########################
# User Data Management #
########################

def mail_registration(recipient_email, first_name, last_name, username, password):
    send_email(
        "MORT | Registration Information",
        [recipient_email],
        render_template("emails/accounts/new-account.html", first_name=first_name, last_name=last_name,
                        username=username, temp_password=password),
        sender_name="MORT Orders"
    )


def mail_forced_password_reset(user, new_password):
    send_email(
        "MORT | Password Reset",
        [user.email],
        render_template("emails/accounts/reset-password.html", first_name=user.first_name, last_name=user.last_name,
                        username=user.username, temp_password=new_password),
        sender_name="MORT Orders"
    )
