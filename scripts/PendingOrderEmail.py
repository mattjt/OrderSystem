#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))
from ConfigParser import SafeConfigParser

import MySQLdb

from OrderSystem import Common
from OrderSystem.utilities.ServerLogger import log_event
from scripts.Email import Email

__author__ = "Matt Turi"
__copyright__ = "Copyright 2016, Mount Olive Robotics Team"
__license__ = "MIT"
__version__ = "0.4"
__maintainer__ = "Matt Turi"
__email__ = "mturi@mort11.org"
__status__ = "Production"

parser = SafeConfigParser()
parser.read(Common.CONFIG_ROOT + "mysql.ini")

connection = MySQLdb.connect(db=parser.get("mysql", "mysql_database"),
                             user=parser.get("mysql", "mysql_user"),
                             passwd=parser.get("mysql", "mysql_password"),
                             host=parser.get("mysql", "mysql_host"))

cursor = connection.cursor()


def main():
    """
    Gets all orders with the pending_approval flag set, and emails the mentor set-up for that subteam a notification
    that they need to approve it
    """

    # Get all subteams
    cursor.execute("SELECT * FROM subteams")

    # For each subteam, mail the subteam mentor a list of pending orders
    for subteam in cursor.fetchall():
        # Select pending orders for given subteam
        cursor.execute(
            "SELECT * FROM orders WHERE (part_for_subteam = %d AND pending_approval = TRUE )" %
            subteam[0])

        # Exit subteam if they have no pending orders
        if cursor.rowcount > 0:
            orders = []
            for order in cursor.fetchall():
                orders.append(order)

            users_to_notify = []

            # Find the subteam mentor(s)
            cursor.execute(
                "SELECT * FROM users WHERE subteam = %d AND can_receive_pending_orders = TRUE;" %
                subteam[0])

            # If there's not mentor to receive the notification, don't process it
            if cursor.rowcount == 0:
                log_event("MAILING-WARNING",
                          "No mentor setup to receive pending order notifications for {0}".format(subteam[1]))
                continue
            else:
                for mentor in cursor.fetchall():
                    users_to_notify.append(mentor[5])

            pending_order_email = Email(
                "MORT | {0} New orders pending approval".format(len(orders)),
                "MORT Orders <orders@mort11.org>",
                users_to_notify
            )
            template = pending_order_email.get_environment().get_template(
                "emails/orders/new/new-pending-order-email.html")
            pending_order_email.set_html(template.render(orders=orders))
            pending_order_email.send()

            log_event("MAILING-INFO", "Finished mailing notifications for {0}!".format(subteam[1]))
        else:
            log_event('MAILING-INFO', "No pending orders to mail for {0}".format(subteam[1]))


if __name__ == '__main__':
    main()
