from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from tgbot.db.database import db


class Keyboards:

    @staticmethod
    def get_start_ikm() -> InlineKeyboardMarkup:
        start_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Каталог продуктов', callback_data='product_catalog')],
            [InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')]
        ])
        return start_ikm

    @staticmethod
    def get_product_catalog() -> InlineKeyboardMarkup:
        cb = CallbackData('categories', 'id', 'action')
        product_catalog_ikm = InlineKeyboardMarkup(row_width=2)
        buttons = []
        for category in db.get_data(table='categories_products'):
            buttons.append(InlineKeyboardButton(text=category[1], callback_data=cb.new(id=category[0], action='category')))
        product_catalog_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return product_catalog_ikm

    @staticmethod
    def get_product_subcatalog(category_id) -> InlineKeyboardMarkup:
        cb = CallbackData('subcategories', 'id', 'action')
        product_subcatalog_ikm = InlineKeyboardMarkup(row_width=3)
        buttons = []
        for subcategory in db.get_data(table='subcategories_products'):
            if subcategory[1] == int(category_id):
                buttons.append(InlineKeyboardButton(text=subcategory[2], callback_data=cb.new(id=subcategory[0], action='subcategory')))
        product_subcatalog_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return product_subcatalog_ikm

    @staticmethod
    def get_products(subcategory_id) -> InlineKeyboardMarkup:
        cb = CallbackData('products', 'id', 'action')
        products_ikm = InlineKeyboardMarkup(row_width=4)
        buttons = []
        for product in db.get_data(table='products'):
            if product[1] == int(subcategory_id):
                buttons.append(InlineKeyboardButton(text=product[2], callback_data=cb.new(id=product[0], action='products')))
        products_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return products_ikm

    @staticmethod
    def get_product(product_id) -> tuple:
        cb = CallbackData('product', 'id', 'action')
        for product in db.get_data(table='products'):
            if product[0] == int(product_id):
                text = f'Название: {product[2]}. \n' \
                       f'Производитель: {product[3]}. \n' \
                       f'Брэнд: {product[4]}. \n' \
                       f'Описание: {product[5]}. \n' \
                       f'Цена: {product[6]}₸. \n'
                photo = product[7]
                product_ikm = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Добавить в корзину', callback_data=cb.new(id=product[0], action='add_to_basket'))],
                    [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
                ])
                return text, product_ikm, photo
        return ()
