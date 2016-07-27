#!/usr/bin/env python
***REMOVED***

import MySQLdb

from OrderSystem import Common
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

connection = MySQLdb.connect(database=parser.get("mysql", "mysql_database"),
                             user=parser.get("mysql", "mysql_user"),
                             password=parser.get("mysql", "mysql_password"),
                             host=parser.get("mysql", "mysql_host"))

cursor = connection.cursorsor()


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
            subteam['id'])

        # Exit subteam if they have no pending orders
        if cursor.rowcount > 0:
            orders_array = []
            for order in cursor.fetchall():
                orders_array.append(order)

            subteam_mentors = []

            # Find the subteam mentor(s)
            cursor.execute(
                "SELECT * FROM users WHERE subteam = %d AND team_role = 'Mentor' AND can_approve_orders = TRUE;" %
                subteam['id'])

            # If there's not mentor to receive the notification, don't process it
            if cursor.rowcount == 0:
                print("No mentor setup to receive pending order notifications for {0}".format(subteam["name"]))
                continue
            else:
                for mentor in cursor.fetchall():
                    subteam_mentors.append(mentor['email'])

            pending_order_email = Email(
                "MORT | {0} New Orders pending approval".format(len(orders_array)),
                "MORT Orders <orders@mort11.org>",
                subteam_mentors
            )
            template = pending_order_email.get_environment().get_template(
                "emails/orders/new/new-pending-order-email.html")
            pending_order_email.set_html(template.render(orders=orders_array))
            pending_order_email.send()

            print("Finished mailing notifications for {0}!".format(subteam['name']))
        else:
            print("WARNING", "No pending orders to mail for {0}".format(subteam['name']))


if __name__ == '__main__':
    main()
