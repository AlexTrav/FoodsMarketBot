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
    end = State()
