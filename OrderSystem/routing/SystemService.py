import csv

from flask import render_template, request, send_file
from flask_classy import FlaskView, route
from flask_login import login_required

from OrderSystem import db, sentry
from OrderSystem.routing.ErrorHandler import get_current_user
from OrderSystem.sql.ORM import Order
from OrderSystem.utilities.ServerLogger import log_event


class SystemService(FlaskView):
    """
    This route will handle doing miscellaneous tasks that involve interacting with the backend.
    I.e. :
    - Generating a data dump
    """

    # Routes will be prefixed by sys-service
    route_base = ""

    @route('/', methods=['GET'])
    @login_required
    def index(self):
        return render_template('sys-service/index.html')

    @route('/data-exporter', methods=['GET', 'POST'])
    @login_required
    def data_exporter(self):
        if request.method == 'POST':
            fiscal_year = request.form.get('fiscal_year')
            csv_path = '/tmp/{0}-fiscal-year-orders.csv'.format(fiscal_year)

            with open(csv_path, 'wb') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)
                writer.writerow(
                    "part_name,part_quantity,part_url,part_unit_price,part_total_price,vendor_name,ordering_subteam,"
                    "part_ordered_on".split(',')
                )

                all_orders_in_fiscal_year = db.session.query(Order).filter(Order.fiscal_year == fiscal_year).order_by(
                    Order.part_ordered_on.asc())

                for order in all_orders_in_fiscal_year:
                    part_name = order.part_name
                    part_quantity = order.part_quantity
                    part_url = order.part_url
                    part_unit_price = order.part_unit_price
                    part_total_price = order.part_total_price
                    vendor_name = order.vendor.vendor_name
                    ordering_subteam_name = order.subteam.name
                    part_ordered_on = order.part_ordered_on

                    writer.writerow([part_name, part_quantity, part_url, part_unit_price, part_total_price, vendor_name,
                                     ordering_subteam_name, part_ordered_on])
            try:
                return send_file(csv_path, as_attachment=True)
            except Exception as e:
                log_event('ERROR', '{0} encountered {1} at {2}'.format(get_current_user(), e, request.path))
                sentry.captureException()
        else:
            return render_template('sys-service/data-exporter.html', page="data_exporter")
