from time import strftime

from flask import render_template, request, url_for, flash, redirect, abort
from flask_classy import FlaskView, route
from flask_login import current_user, login_required
from sqlalchemy import and_
from sqlalchemy.orm.exc import UnmappedInstanceError

from ErrorHandler import get_current_user
from OrderSystem import db, sentry
from OrderSystem import forms
from OrderSystem.routing.CRUDBase import CRUDBase
from OrderSystem.sql.ORM import Order, Subteam, Vendor
from OrderSystem.utilities.Helpers import flash_errors, get_fiscal_year, strip_non_ascii
from OrderSystem.utilities.Permissions import update_order_status_access_required, approve_order_access_required
from OrderSystem.utilities.ServerLogger import log_event


class OrderBackend(FlaskView, CRUDBase):
    """
    The OrderSystem handles all of MORT's part ordering, vendor management, and mentor/treasurer mailings.
    Our budget system is implemented in another class
    """

    # Configure routing for Order sub-component. All OrderSystem routes are prefixed with /orders
    route_base = ""

    @route('/create', methods=['GET', 'POST'])
    @login_required
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
                fiscal_year = get_fiscal_year()['current_fiscal_year']
                vendor_id = request.form['vendor']
                part_name = strip_non_ascii(order_form.part_name.data)
                part_url = strip_non_ascii(order_form.part_url.data)
                part_number = strip_non_ascii(order_form.part_number.data)
                part_quantity = int(order_form.part_quantity.data)
                part_unit_price = float(order_form.part_unit_price.data)
                part_total_price = round(part_quantity * part_unit_price, 2)
                part_needed_by = order_form.needed_by.data
                part_for_subteam = request.form['for_subteam']
                part_ordered_by = current_user.id
                part_ordered_on = strftime("%m/%d/%Y")
                total = part_total_price

                db.session.add(
                    Order(fiscal_year, vendor_id, part_name, part_url, part_number, part_quantity,
                          part_unit_price, part_total_price, part_needed_by, part_for_subteam,
                          part_ordered_by, part_ordered_on, total)
                )
                db.session.commit()

                return redirect(url_for('OrderBackend:index', order_status="unprocessed"))
            except Exception as e:
                log_event('ERROR', '{0} encountered {1} at {2}'.format(get_current_user(), e, request.path))
                sentry.captureException()
                db.session.rollback()
                flash(
                    "Unknown database error! [{0}]. Please contact a system administrator if the issue persists".format(
                        e), 'error')  # TODO Get a better error code for this
        else:
            flash_errors(order_form)
        return render_template('orders/manage/new-order.html', today_date=strftime("%m/%d/%Y"), form=order_form,
                               subteams=subteams, vendors=vendors, page="new_order")

    @route('/<order_status>')
    @login_required
    def index(self, order_status):
        """
        Shows the user an overview of all unprocessed, in progress, and completed orders.

        @note OrderSystem will only show orders that have been approved from pending by the OSA or the subteam mentor
        @return: OrderSystem home page
        """
        orders = db.session.query(Order).filter(
            Order.pending_approval == False,
            Order.fiscal_year == get_fiscal_year()['current_fiscal_year'],
            Order.order_status == order_status
        ).order_by(Order.part_ordered_on.asc())

        # Python switch-case equivalent
        return_template = {
            "unprocessed": "unprocessed.html",
            "in-progress": "in-progress.html",
            "shipped": "shipped.html",
            "completed": "completed.html",
        }

        return render_template('orders/view/{0}'.format(return_template.get(order_status, "invalid-type.html")),
                               today_date=strftime("%m-%d-%Y"), orders=orders, num_of_orders=orders.count(),
                               page="orders_" + order_status)

    @route('/single/<order_id>')
    @login_required
    def single_order_view(self, order_id):
        """
        Shows the user a single order given an order ID

        @return: Single order view
        """
        order = db.session.query(Order).filter(Order.id == order_id).first()

        return render_template('orders/view/single-order-view.html', order=order, page="orders")

    @route('/update/<string:order_status>/<int:order_id>', methods=['GET', 'POST'])
    @login_required
    def update(self, order_status, order_id):
        """
        Updates an existing order, at whatever stage it may be in

        @note Should probably check with Treasurer if they want to lockout student modification of orders that are past
        the not processed point
        @return: Redirect to OrderSystem index if successful
        """

        try:
            order = db.session.query(Order).filter(Order.id == order_id).first()

            if order.part_ordered_by == current_user.id or current_user.is_admin or (
                    current_user.subteam == order.part_for_subteam and current_user.can_approve_orders):
                # Get available vendors and sort alphabetically
                vendors = db.session.query(Vendor).order_by(Vendor.vendor_name)

                # Get subteams that are actual subteams
                subteams = db.session.query(Subteam).all()

                form = forms.Order(request.form)
                if form.validate_on_submit():
                    vendor_id = request.form['vendor']

                    part_name = strip_non_ascii(form.part_name.data)
                    part_url = strip_non_ascii(form.part_url.data)
                    part_number = strip_non_ascii(form.part_number.data)
                    part_quantity = float(form.part_quantity.data)
                    part_unit_price = float(form.part_unit_price.data)
                    part_total_price = round((part_unit_price * part_quantity), 2)
                    part_needed_by = form.needed_by.data
                    part_for_subteam = request.values['for_subteam']

                    order.vendor_id = vendor_id
                    order.part_name = part_name
                    order.part_url = part_url
                    order.part_number = part_number
                    order.part_quantity = part_quantity
                    order.part_unit_price = part_unit_price
                    order.part_total_price = part_total_price
                    order.part_needed_by = part_needed_by
                    order.part_for_subteam = part_for_subteam

                    part_shipping_cost = float(order.part_shipping_cost)
                    part_credit = float(order.credit)

                    # Check permissions and that field aren't empty
                    if current_user.can_update_order_status:
                        shipping = request.values['shipping']
                        if shipping != '':
                            part_shipping_cost = float(shipping)

                        credit = request.values['credit']
                        if credit != '':
                            part_credit = float(credit)

                    order.part_shipping_cost = part_shipping_cost
                    total = round(((part_unit_price * part_quantity) + part_shipping_cost) - part_credit, 2)
                    order.credit = part_credit
                    order.total = total

                    db.session.commit()
                    if order_status == "pending":
                        return redirect(url_for('PendingOrders:index'))
                    else:
                        return redirect(url_for('OrderBackend:index', order_status=order_status))

                else:
                    flash_errors(form)
                return render_template('orders/manage/edit-order.html', order=order, form=form, vendors=vendors,
                                       subteams=subteams, page="orders")
            else:
                flash("You can't edit an order that you didn't create!", 'error')
                return redirect(url_for('OrderBackend:index', order_status=order_status))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)

    @route('/delete/<string:order_status>/<int:order_id>', methods=['GET'])
    @login_required
    def delete(self, order_status, order_id):
        """
        Delete an existing order

        @return: Redirect to OrderSystem index
        """
        order_to_delete = db.session.query(Order).filter(Order.id == order_id).first()

        if order_to_delete.part_ordered_by != current_user.id and not current_user.is_admin:
            flash("You can't delete an order that you didn't place!", "error")
            return redirect(url_for('OrderBackend:index', order_status=order_status))

        try:
            db.session.delete(order_to_delete)
            db.session.commit()
            flash("Successfully deleted order!", "success")
            return redirect(url_for('OrderBackend:index', order_status=order_status))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            db.session.rollback()
            flash("Error deleting order! [{0}]".format(e), 'error')
            return redirect(url_for('OrderBackend:index', order_status=order_status))

    # #################### NON-CRUD METHODS #################### #

    @route('/update-part-status', methods=['GET', 'POST'])
    @update_order_status_access_required
    def update_part_status(self):
        """
        Changes the status of a part. Available part statuses are Unprocessed, In Progress, Shipped, and Completed

        @return: Nothing. Method is called from some type of asynchronous segment of code
        """
        try:
            allowable_statuses = ['unprocessed', 'in-progress', 'shipped', 'completed']
            item_id = request.values['oID']
            current_status = request.values['currentStatus']
            new_status = request.values['updatedStatus']

            if new_status in allowable_statuses:
                item = db.session.query(Order).filter(Order.id == item_id).first()
                if item is not None:
                    item.order_status = str(new_status).lower().replace(" ", "-")
                    db.session.commit()
                    flash("Successfully updated order status", 'success')
                    return redirect(url_for('OrderBackend:index', order_status=current_status))
                else:
                    flash("ERROR! Order requested was not found!", 'error')
                    return redirect(url_for('OrderBackend:index', order_status=current_status))
            else:
                flash("ERROR! Invalid order status was provided!", 'error')
                return redirect(url_for('OrderBackend:index', order_status=current_status))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()
            abort(500)


class Vendors(FlaskView, CRUDBase):
    """
    The Vendors class manages the vendors available for team members to enter in the OrderSystem

    @note Future plans
    - Add method that will show the user all parts ordered from a specified vendor
    """

    route_base = ""

    @route('/create', methods=['GET', 'POST'])
    @login_required
    def create(self):
        """
        Provides the user with a menu to create a new vendor

        @return: Redirects to the Vendors index if successful
        """

        vendor_form = forms.NewVendor(request.form)

        try:
            if vendor_form.validate_on_submit():
                db.session.add(Vendor(vendor_form.vendor_name.data, vendor_form.vendor_url.data,
                                      vendor_form.vendor_email.data if vendor_form.vendor_email.data != "" else "None",
                                      vendor_form.vendor_phone.data if vendor_form.vendor_phone.data != "" else "None"))
                db.session.commit()
                return redirect(url_for('Vendors:index'))
            else:
                flash_errors(vendor_form)
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()

        return render_template('settings/vendors/add-vendor.html', form=vendor_form, page="vendors")

    @route('/index')
    @login_required
    def index(self):
        """
        Shows the user vendors currently entered into the system

        @return: A list of the available vendors
        """
        vendors = db.session.query(Vendor).order_by(Vendor.vendor_name)
        return render_template('settings/vendors/vendors.html', vendors=vendors, page="vendors")

    @route('/update/<int:vendor_id>', methods=['GET', 'POST'])
    @login_required
    def update(self, vendor_id):
        """
        Updates an existing vendor

        @return: Redirect to Vendors index if successful
        """
        try:
            vendor = db.session.query(Vendor).filter(Vendor.id == vendor_id).first()

            vendor_form = forms.NewVendor(request.form)

            if vendor_form.validate_on_submit():
                vendor.vendor_name = vendor_form.vendor_name.data
                vendor.vendor_url = vendor_form.vendor_url.data
                vendor.vendor_email = vendor_form.vendor_email.data
                vendor.vendor_phone = vendor_form.vendor_phone.data
                db.session.commit()
                return redirect(url_for('Vendors:index'))
        except Exception as e:
            log_event("ERROR", e)
            sentry.captureException()

        return render_template('settings/vendors/edit-vendor.html', form=vendor_form, vendor=vendor, page="vendors")

    @route('/delete/<int:vendor_id>', methods=['GET'])
    @login_required
    def delete(self, vendor_id):
        """
        Delete a vendor

        @return: Redirect to Vendors index if successful
        """
        vendor_to_delete = db.session.query(Vendor).filter(Vendor.id == vendor_id).first()

        try:
            db.session.delete(vendor_to_delete)
            db.session.commit()
        except:
            flash(
                "You can't delete this! There are orders that are dependant on this vendor! Please delete them first!",
                'warning')
        return redirect(url_for('Vendors:index'))


class PendingOrders(FlaskView, CRUDBase):
    """
    The Pending Order system provides a means for subteam mentors and OrderSystem admins to view orders that students
    place and verify them before they are actually sent off for processing by the Treasurer
    """

    route_base = ""

    def create(self):
        """
        No implementation
        """
        pass

    @route('/index')
    @login_required
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
        if current_user.can_receive_order_notifications or current_user.is_admin:
            # User is an OrderSystem admin
            orders_for_subteam = db.session.query(Order).filter(Order.pending_approval == True)
            is_order_system_admin = True
        else:
            # User is a normal mentor
            orders_for_subteam = db.session.query(Order).filter(and_(
                Order.part_for_subteam == current_user.subteam, Order.pending_approval == True))
        return render_template('orders/pending/index.html', orders=orders_for_subteam, page="pending_orders",
                               is_order_system_admin=is_order_system_admin)

    @route('/approve/<int:order_id>')
    @approve_order_access_required
    def update(self, order_id):
        """
        Approve an order and send it off for processing by Treasurer

        @return: Redirect to PendingOrders index
        """
        order_to_approve = db.session.query(Order).filter(Order.id == order_id).first()
        try:
            # If the user is an admin, or is a member of that subteam, they can approve the order
            if current_user.is_admin or current_user.subteam_ref.id == order_to_approve.part_for_subteam:
                if not order_to_approve == None:
                    order_to_approve.pending_approval = False
                    order_to_approve.approved_by = current_user.id
                    db.session.commit()
                    flash("Successfully approved order!", 'success')
                else:
                    flash("You tried to approve/deny a non-existent order", 'error')
            else:
                flash("You can't approve an order that isn't made on your subteam's behalf!")
        except:
            sentry.captureException()

        return redirect(url_for('PendingOrders:index'))

    @route('/deny/<int:order_id>')
    @login_required
    def delete(self, order_id):
        """
        Deny an order and have it deleted

        @return: Redirect to PendingOrders index
        """
        order_to_deny = db.session.query(Order).filter(Order.id == order_id).first()
        try:
            # If the user is an admin, or is a member of that subteam, they can approve the order
            if current_user.is_admin or current_user.subteam_ref.id == order_to_deny.part_for_subteam:
                try:
                    db.session.delete(order_to_deny)
                    db.session.commit()
                    flash("Successfully denied order!", 'warning')
                except UnmappedInstanceError:
                    flash("You tried to approve/deny a non-existent order", 'error')
            else:
                flash("You can't deny an order that isn't made on your subteam's behalf!", 'error')
        except:
            sentry.captureException()

        return redirect(url_for('PendingOrders:index'))
