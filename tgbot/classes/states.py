from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStatesGroup(StatesGroup):
    start = State()
    product_catalog = State()
    product_subcatalog = State()
    products = State()
    product = State()
    adding_to_basket = State()
    my_basket = State()
    edit_basket = State()
    place_an_order = State()
    my_orders = State()
    order_item = State()
    add_address = State()
    work = State()
    search = State()
    my_profile = State()
    add_phone = State()
    list_admins = State()


class OperatorStatesGroup(StatesGroup):
    state = ''
    start = State()
    working_warehouse = State()
    search = State()
    search_id = State()
    product = State()
    change_price = State()
    add_product = State()
    select_subcategory = State()


class CourierStatesGroup(StatesGroup):
    start = State()
    orders = State()
    order_item = State()


class AdminStatesGroup(StatesGroup):
    start = State()
    users = State()
    give_role_user = State()
    add_balance = State()
    add_balance_user = State()
    # search_user = State()
    documents = State()
    document = State()
