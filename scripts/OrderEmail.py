#!/usr/bin/env python
***REMOVED***

from OrderSystem import Common
from OrderSystem.utilities.Helpers import get_order_notification_recipients
from scripts.Email import Email
import MySQLdb

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

cursor = connection.cursor()


def main():
    cursor.execute("SELECT * FROM orders WHERE (order_dirty = TRUE AND pending_approval = FALSE);")

    if cursor.rowcount > 0:
        orders = []
        for order in cursor.fetchall():
            orders.append(order)

        cursor.execute("UPDATE orders SET order_dirty = FALSE;")
        connection.commit()

        order_email = Email("MORT | {0} New Orders".format(len(orders)), "MORT Orders <orders@mort11.org>",
                            get_order_notification_recipients())
        template = order_email.get_environment().get_template("emails/orders/new/new-order-email.html")
        order_email.set_html(template.render(orders=orders))
        order_email.send()

        print("Finished mailing dirty orders")
    else:
        print("No orders to process")


if __name__ == '__main__':
    main()
