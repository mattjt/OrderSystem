from decimal import Decimal

from flask import render_template
from flask.ext.classy import FlaskView, route
from sqlalchemy import and_
from werkzeug.utils import redirect

from OrderBackend import db
from OrderBackend import forms
from OrderBackend.routing.CRUDBase import CRUDBase
from OrderBackend.sql.ORM import Budget, Subteam, Order
from OrderBackend.utilities.Helpers import flash_errors
from OrderBackend.utilities.Permissions import order_admin_access_required, order_view_access_required


class Budgets(FlaskView, CRUDBase):
    """
    The Budgets system provides team members with a way to view how much money their subteam still has available, as
    well as drilling down into individual subteams and specific orders
    """

    route_base = ""

    BUDGET_FULL_THRESH = 0.75  # 75%
    BUDGET_MEDIUM_THRESH = 0.50  # 50%
    BUDGET_LOW_THRESH = 0.25  # 25%

    def create(self):
        """
        No implementation
        """
        pass

    @route('/<fiscal_year>')
    @order_view_access_required
    def index(self, fiscal_year):
        """
        Shows the user an overview of the budgets for subteams this year

        @param fiscal_year: The current FRC season
        @return: List of subteams color-coded with their amount of money remaining
        """
        subteams = db.session.query(Subteam).filter(Subteam.hidden_from_budgets_list == False).order_by(
            Subteam.id.asc())

        ids = []
        names = []
        css_classes = []
        cash_left = []
        started_with = []

        for subteam in subteams:
            try:
                budget = db.session.query(Budget).filter(
                    and_(Budget.fiscal_year == fiscal_year, Budget.subteam_id == subteam.id)).first()

                curr_orders = db.session.query(Order).filter(
                    and_(Order.fiscal_year == fiscal_year, Order.part_for_subteam == subteam.id,
                         Order.pending_approval is False))

                dollars_left = Decimal(budget.dollar_amount)
                for order in curr_orders:
                    dollars_left -= Decimal(order.total)

                # Decide what class to use
                if (dollars_left / budget.dollar_amount) > self.BUDGET_FULL_THRESH:
                    css_class = "budget-full"
                elif self.BUDGET_MEDIUM_THRESH < (dollars_left / budget.dollar_amount) < self.BUDGET_FULL_THRESH:
                    css_class = "budget-low"
                elif self.BUDGET_LOW_THRESH < (dollars_left / budget.dollar_amount) < self.BUDGET_MEDIUM_THRESH:
                    css_class = "budget-verylow"
                elif 0 < (dollars_left / budget.dollar_amount) < self.BUDGET_LOW_THRESH:
                    css_class = "budget-critical"
                else:
                    css_class = "budget-empty"
                ids.append(subteam.id)
                names.append(subteam.name)
                css_classes.append(css_class)
                cash_left.append('{0:.2f}'.format(dollars_left))
                started_with.append('{0:.2f}'.format(budget.dollar_amount))
            except:
                ids.append(subteam.id)
                names.append(subteam.name)
                css_classes.append("")
                cash_left.append(0)
                started_with.append(0)

        return render_template('orders/budgets/index.html', subteams=names, cash_left=cash_left,
                               started_with=started_with, css_classes=css_classes, fiscal_year=fiscal_year, ids=ids,
                               thresholds=[self.BUDGET_FULL_THRESH, self.BUDGET_MEDIUM_THRESH, self.BUDGET_LOW_THRESH])

    @route('/<fiscal_year>/<subteam_id>/set', methods=['GET', 'POST'])
    @order_admin_access_required
    def update(self, subteam_id, fiscal_year):
        """
        Changes the amount of money that a subteam is marked as having available

        @param subteam_id: The database-given ID of the subteam to update the budget of
        @param fiscal_year: The current FRC season
        @return: Redirect to Budgets index
        """

        form = forms.SetBudgetForm()

        existing_budget = db.session.query(Budget).filter(Budget.subteam_id == subteam_id).first()

        if form.validate_on_submit():
            if existing_budget is None:
                # Subteam didn't have a budget previously set
                db.session.add(Budget(subteam_id, form.amount.data, fiscal_year))
            else:
                # Subteam had an existing budget; update the previous one instead of creating a new DB row
                existing_budget.dollar_amount = form.amount.data

            db.session.commit()
            return redirect('/orders/budgets/%s' % fiscal_year)

        else:
            flash_errors(form)

        return render_template('orders/budgets/set.html', form=form)

    def delete(self):
        """
        No implementation
        """
        pass

    @route('/<fiscal_year>/<subteam_id>')
    @order_view_access_required
    def view_orders_by_subteam(self, fiscal_year, subteam_id):
        """
        Shows a list of orders for the given subteam

        @param subteam_id: The database-given ID of the subteam to update the budget of
        @param fiscal_year: The current FRC season
        @return: List of all orders for the given subteam, along with the member who ordered the part, and other info
        """
        orders_by_subteam = db.session.query(Order).filter(
            and_(Order.fiscal_year == fiscal_year, Order.part_for_subteam == subteam_id,
                 Order.pending_approval is False))

        subteam = db.session.query(Subteam).filter(Subteam.id == subteam_id).first()

        total = 0
        for order in orders_by_subteam:
            total += order.total

        return render_template('orders/budgets/orders-by-subteam.html', orders_by_subteam=orders_by_subteam,
                               total=total, subteam=subteam)
