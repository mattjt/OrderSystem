from OrderSystem import app
from OrderSystem.routing import errors
from OrderSystem.routing.Budgets import Budgets
from OrderSystem.routing.OrderBackend import OrderBackend, Vendors, PendingOrders
from OrderSystem.routing.Users import Users
from OrderSystem.routing.admin import admin
from OrderSystem.routing.auth import auth
from OrderSystem.routing.core import main
from OrderSystem.utilities.ServerLogger import console_print


def init():
    app.register_blueprint(main)
    console_print('INFO', 'Loaded core routes', always_show=False)

    app.register_blueprint(admin)
    console_print('INFO', 'Loaded admin routes', always_show=False)

    app.register_blueprint(auth)
    console_print('INFO', 'Loaded authentication routes', always_show=False)

    OrderBackend.register(app, route_prefix='/orders', trailing_slash=False)
    Vendors.register(app, route_prefix='/orders/vendors', trailing_slash=False)
    PendingOrders.register(app, route_prefix='/orders/pending', trailing_slash=False)
    Budgets.register(app, route_prefix='/orders/budgets', trailing_slash=False)
    console_print('INFO', 'Loaded order system routes', always_show=False)

    Users.register(app, route_prefix="/user", trailing_slash=False)
    console_print('INFO', 'Loaded user routes', always_show=False)

    errors.init()
    console_print('INFO', 'Loaded error routes', always_show=False)
