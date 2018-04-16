from OrderSystem import app
from OrderSystem.routing import ErrorHandler
from OrderSystem.routing.Admin import Admin, UserManager, SubteamManager
from OrderSystem.routing.Authentication import auth
from OrderSystem.routing.Budgets import Budgets
from OrderSystem.routing.Core import main
from OrderSystem.routing.OrderBackend import OrderBackend, Vendors, PendingOrders
from OrderSystem.routing.SystemService import SystemService
from OrderSystem.routing.Users import Users
from OrderSystem.utilities.ServerLogger import console_print


def init():
    app.register_blueprint(main)
    console_print('INFO', 'Loaded core routes', always_show=False)

    app.register_blueprint(auth)
    console_print('INFO', 'Loaded authentication routes', always_show=False)

    Admin.register(app, route_prefix="/admin", trailing_slash=False)
    UserManager.register(app, route_prefix="/admin/users", trailing_slash=False)
    SubteamManager.register(app, route_prefix="/admin/subteams", trailing_slash=False)
    console_print('INFO', 'Loaded admin routes', always_show=False)

    OrderBackend.register(app, route_prefix='/orders', trailing_slash=False)
    Vendors.register(app, route_prefix='/orders/vendors', trailing_slash=False)
    PendingOrders.register(app, route_prefix='/orders/pending', trailing_slash=False)
    Budgets.register(app, route_prefix='/orders/budgets', trailing_slash=False)
    console_print('INFO', 'Loaded order system routes', always_show=False)

    Users.register(app, route_prefix="/user", trailing_slash=False)
    console_print('INFO', 'Loaded user routes', always_show=False)

    SystemService.register(app, route_prefix="/sys-service", trailing_slash=False)
    console_print('INFO', 'Loaded system service interface', always_show=False)

    ErrorHandler.init()
    console_print('INFO', 'Loaded error routes', always_show=False)
