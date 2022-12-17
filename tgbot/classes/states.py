from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStatesGroup(StatesGroup):
    start = State()
    product_catalog = State()
    product_subcatalog = State()
    products = State()
    product = State()
    my_orders = State()

