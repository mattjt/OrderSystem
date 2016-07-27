import datetime
from time import strftime

from django.shortcuts import redirect
from flask import render_template, request, url_for, flash
from flask.ext.classy import FlaskView, route
from flask.ext.login import current_user
from sqlalchemy import or_, and_

from OrderSystem import db
from OrderSystem import forms
from OrderSystem.routing.CRUDBase import CRUDBase
from OrderSystem.sql.ORM import Order, Subteam, Vendor
from OrderSystem.utilities.Helpers import flash_errors
from OrderSystem.utilities.Permissions import order_view_access_required, order_edit_access_required, \
    update_order_status_required, approve_order_required


class OrderBackend(FlaskView, CRUDBase):
    """
    The OrderSystem handles all of MORT's part ordering, vendor management, and mentor/treasurer mailings.
    Our budget system is implemented in another class
    """

    # Configure routing for Order sub-component. All OrderSystem routes are prefixed with /orders
    route_base = ""

    today_date = strftime("%m-%d-%Y")  # Month/Day/Year Format
    this_year = datetime.datetime.today().year

    @route('/create', methods=['GET', 'POST'])
    @order_edit_access_required
    def create(self):
        """
        Creates a new order from user input, records it to the database, and queues it up to be emailed to subteam
        mentors/treasurer

        @return: Redirect back to orders index on successful completion
        """

        # Get all subteams
        subteams = db.session.query(Subteam).all()

        # Get vendors list alphabetically
        vendors = db.session.query(Vendor).order_by(Vendor.vendor_name)
        order_form = forms.Order(request.form)

        if order_form.validate_on_submit():
            try:
                fiscal_year = self.this_year
                vendor_id = request.form['vendor']
                part_name = order_form.part_name.data
                part_url = order_form.part_url.data
                part_number = order_form.part_number.data
                part_quantity = int(order_form.part_quantity.data)
                part_unit_price = float(order_form.part_unit_price.data)
                part_total_price = round(part_quantity * part_unit_price, 2)
                part_needed_by = order_form.needed_by.data
                part_for_subteam = request.form['for_subteam']
                part_ordered_by = request.form['ordered_by']
                part_ordered_on = order_form.ordered_on.data
                total = part_total_price

                db.session.add(
                    Order(fiscal_year, vendor_id, part_name, part_url, part_number, part_quantity,
                          part_unit_price, part_total_price, part_needed_by, part_for_subteam,
                          part_ordered_by, part_ordered_on, total)
                ).commit()

                return redirect(url_for('orders.index'))
            except Exception as e:
                db.session.rollback()
                flash("Unknown database error! [{0}]".format(e))  # TODO Get a better error code for this
        else:
            flash_errors(order_form)
        return render_template('orders/new-order.html', today_date=self.today_date, form=order_form, subteams=subteams,
                               vendors=vendors)

    @route('/index')
    @order_view_access_required
    def index(self):
        """
        Shows the user an overview of all unprocessed, in progress, and completed orders.

        @note OrderSystem will only show orders that have been approved from pending by the OS admin or the subteam
        mentor
        @return: OrderSystem home page
        """
        all_orders = db.session.query(Order).filter(
            Order.pending_approval is False,
            or_(Order.fiscal_year == self.this_year, Order.fiscal_year == self.this_year - 1)
        ).order_by(Order.id.desc())

        return render_template('orders/index.html', today_date=strftime("%m-%d-%Y"), orders=all_orders,
                               this_year=self.this_year)

    @route('/update/<self>', methods=['GET', 'POST'])
    @order_edit_access_required
    def update(self):
        """
        Updates an existing order, at whatever stage it may be in

        @note Should probably check with Treasurer if they want to lockout student modification of orders that are past
        the not processed point
        @return: Redirect to OrderSystem index if successful
        """

        # Return 404 if the supplied order ID doesn't exist
        order_to_update = db.session.query(Order).filter(Order.id == self).first_or_404()

        # Get available vendors and sort alphabetically
        available_vendors = db.session.query(Vendor).order_by(Vendor.vendor_name)

        # Get subteams that are actual subteams
        available_subteams = db.session.query(Subteam).filter(Subteam.hidden_from_budgets_list is False)

        order_form = forms.Order(request.form)

        if order_form.validate_on_submit():
            try:
                fiscal_year = order_form.fiscal_year.data

                vendor_id = request.form['vendor']

                part_name = order_form.part_name.data
                part_url = order_form.part_url.data
                part_no = order_form.part_number.data
                part_quantity = int(request.form['part_quantity'])
                part_unit_price = float(request.form['part_unit_price'])
                part_shipping_cost = float(request.form['part_shipping_cost'])
                part_credit = float(request.form['part_credit'])
                part_total_price = round(((part_unit_price * part_quantity) + part_shipping_cost) - part_credit, 2)

                part_needed_by = order_form.needed_by.data
                part_for_subteam = request.form['for_subteam']
                part_ordered_by = request.form['ordered_by']
                part_ordered_on = order_form.ordered_on.data

                total = part_total_price

                order_to_update.fiscal_year = fiscal_year
                order_to_update.vendor_id = vendor_id
                order_to_update.part_name = part_name
                order_to_update.part_url = part_url
                order_to_update.part_no = part_no
                order_to_update.part_quantity = part_quantity
                order_to_update.part_unit_price = part_unit_price
                order_to_update.part_total_price = part_total_price
                order_to_update.part_shipping_cost = part_shipping_cost
                order_to_update.part_needed_by = part_needed_by
                order_to_update.part_for_subteam = part_for_subteam
                order_to_update.part_ordered_by = part_ordered_by
                order_to_update.part_ordered_on = part_ordered_on
                order_to_update.credit = part_credit
                order_to_update.total = total

                db.session.commit()

                return redirect(url_for('orders.index'))
            except Exception as e:
                db.session.rollback()
                flash("Unknown database error! [{0}]".format(e))
        else:
            flash_errors(order_form)
        return render_template('orders/edit-order.html', order=order_to_update, form=order_form,
                               vendors=available_vendors, subteams=available_subteams)

    @route('/delete/<self>', methods=['GET'])
    @order_edit_access_required
    def delete(self):
        """
        Delete an existing order

        @return: Redirect to OrderSystem index
        """
        order_to_delete = db.session.query(Order).filter(Order.id == self).first_or_404()

        try:
            db.session.delete(order_to_delete).commit()
            return redirect(url_for('orders.index'))
        except:
            db.session.rollback()
            flash("Error deleting order!")
            return redirect(url_for('orders.index'))

    # #################### NON-CRUD METHODS #################### #

    @route('/update-part-status', methods=['GET', 'POST'])
    @update_order_status_required
    def update_part_status(self):
        """
        Changes the status of a part. Available part statuses are Not Processed, In Progress, Shipped, and Completed

        @return: Nothing. Method is called from some type of asynchronous segment of code
        """
        item_id = request.values['oId']
        new_status = request.values['newTable']

        item = db.session.query(Order).filter(Order.id == item_id).first_or_404()

        item.order_status = new_status
        db.session.commit()
        return "Successfully updated order status!"


class Vendors(FlaskView, CRUDBase):
    """
    The Vendors class manages the vendors available for team members to enter in the OrderSystem

    @note Future plans
    - Add method that will show the user all parts ordered from a specified vendor
    """

    route_base = ""

    @route('/create', methods=['GET', 'POST'])
    @order_edit_access_required
    def create(self):
        """
        Provides the user with a menu to create a new vendor

        @return: Redirects to the Vendors index if successful
        """

        vendor_form = forms.NewVendor(request.form)

        try:
            if vendor_form.validate_on_submit():
                vendor = Vendor(vendor_form.vendor_name.data, vendor_form.vendor_url.data,
                                vendor_form.vendor_email.data, vendor_form.vendor_phone.data)
                db.session.add(vendor).commit()
                return redirect(url_for('vendors.index'))
            else:
                flash_errors(vendor_form)
        except:
            db.session.rollback()
            flash("Vendor with same name probably already exists!")

        return render_template('orders/vendors/add.html', form=vendor_form)

    @route('/index')
    @order_view_access_required
    def index(self):
        """
        Shows the user vendors currently entered into the system

        @return: A list of the available vendors
        """
        all_vendors = db.session.query(Vendor).order_by(Vendor.vendor_name)
        return render_template('orders/vendors/index.html', vendors=all_vendors)

    @route('/update/<self>', methods=['GET', 'POST'])
    @order_edit_access_required
    def update(self):
        """
        Updates an existing vendor

        @return: Redirect to Vendors index if successful
        """
        vendor = db.session.query(Vendor).filter(Vendor.id == self).first_or_404()

        vendor_form = forms.NewVendor(request.form)

        try:
            if vendor_form.validate_on_submit():
                vendor.vendor_name = vendor_form.vendor_name.data
                vendor.vendor_url = vendor_form.vendor_url.data
                vendor.vendor_email = vendor_form.vendor_email.data
                vendor.vendor_phone = vendor_form.vendor_phone.data
                db.session.commit()
                return redirect(url_for('vendors.index'))
        except:
            flash("Vendor with same name probably already exists!")
        return render_template('orders/vendors/edit.html', form=vendor_form, vendor=vendor)

    @route('/delete/<self>', methods=['GET'])
    @order_edit_access_required
    def delete(self):
        """
        Delete a vendor

        @return: Redirect to Vendors index if successful
        """
        vendor_to_delete = db.session.query(Vendor).filter(Vendor.id == self).first()

        try:
            db.session.delete(vendor_to_delete).commit()
        except:
            flash(
                "You can't delete this! There are orders that are dependant on this vendor! Please delete them first!")
        return redirect(url_for('vendors.index'))


class PendingOrders(FlaskView, CRUDBase):
    """
    The Pending Order system provides a means for subteam mentors and OrderSystem admins to view orders that students
    place and verify them before they are actually sent off for processing by the Treasurer
    """

    route_base = ""

    @approve_order_required
    def create(self):
        """
        No implementation
        """
        pass

    @route('/index')
    @approve_order_required
    def index(self):
        """
        Shows a mentor a list of all orders that are currently pending for their subteam.
        Shows an OrderSystem admin a list of orders that are currently pending for all subteams

        @note OrderSystem admins are based off of either of two permission nodes. That permission is granted if the
        user is a System Administrator (SysAdmin), or if the user has the ability to receive order notifications. The
        only users who should be receiving order notifications are the treasurer, the Head Mentor (should they want to),
        and any senior developer who is deemed necessary

        @return: A list of pending orders
        """

        is_order_system_admin = False
        if current_user.receive_order_notifications or current_user.is_admin:
            # User is an OrderSystem admin
            orders_for_subteam = db.session.query(Order).filter(Order.pending_approval is True)
            is_order_system_admin = True
        else:
            # User is a normal mentor
            orders_for_subteam = db.session.query(Order).filter(and_(
                Order.part_for_subteam == current_user.subteam,
                Order.pending_approval is True)
            )
        return render_template('orders/pending-orders/index.html', orders=orders_for_subteam,
                               is_order_system_admin=is_order_system_admin)

    @route('/approve/<order_id>')
    @approve_order_required
    def update(self, order_id):
        """
        Approve an order and send it off for processing by Treasurer

        @return: Redirect to PendingOrders index
        """
        approved_order = db.session.query(Order).filter(Order.id == order_id).first_or_404()
        approved_order.pending_approval = False
        db.session.commit()
        flash("Successfully approved order!")
        return redirect(url_for('pending_orders.index'))

    @route('/deny/<order_id>')
    @approve_order_required
    def delete(self, order_id):
        """
        Deny an order and have it deleted

        @return: Redirect to PendingOrders index
        """
        denied_order = db.session.query(Order).filter(Order.id == order_id).first_or_404()
        db.session.delete(denied_order).commit()
        flash("Successfully denied order!")
        return redirect(url_for('pending_orders.index'))
