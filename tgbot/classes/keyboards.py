from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from tgbot.db.database import db


class Keyboards:

    @staticmethod
    def get_start_ikm() -> InlineKeyboardMarkup:
        start_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Каталог продуктов', callback_data='product_catalog')],
            [InlineKeyboardButton(text='Моя корзина', callback_data='my_basket')],
            [InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')],
            [InlineKeyboardButton(text='Глобальный поиск', callback_data='search')],
            [InlineKeyboardButton(text='Работа', callback_data='work')]
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
    def get_product_subcatalog(category_id: int) -> InlineKeyboardMarkup:
        cb = CallbackData('subcategories', 'id', 'action')
        product_subcatalog_ikm = InlineKeyboardMarkup(row_width=3)
        buttons = []
        for subcategory in db.get_data(table='subcategories_products'):
            if subcategory[1] == int(category_id):
                buttons.append(InlineKeyboardButton(text=subcategory[2],callback_data=cb.new(id=subcategory[0], action='subcategory')))
        product_subcatalog_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return product_subcatalog_ikm

    @staticmethod
    def get_products(subcategory_id: int) -> InlineKeyboardMarkup:
        cb = CallbackData('products', 'id', 'action')
        products_ikm = InlineKeyboardMarkup(row_width=3)
        buttons = []
        for product in db.get_data(table='products'):
            if product[1] == int(subcategory_id):
                buttons.append(InlineKeyboardButton(text=product[2], callback_data=cb.new(id=product[0], action='products')))
        products_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return products_ikm

    @staticmethod
    def get_product(product_id: int, user_id: int, states_previous=None, back_id=None) -> tuple:
        cb = CallbackData('product', 'id', 'action')
        for product in db.get_data(table='products'):
            if product[0] == int(product_id):
                if back_id is None:
                    back_id = -1
                if states_previous == 'UserStatesGroup:edit_basket':
                    back_id = -2
                text = f'Название: {product[2]}. \n'
                if product[3] != '':
                    text += f'Производитель: {product[3]}. \n'
                if product[4] != '':
                    text += f'Брэнд: {product[4]}. \n'
                if product[5] != '':
                    text += f'Описание: {product[5]} \n'
                text += f'Цена: {product[6]}₸. \n'
                photo = product[7]
                entries = db.get_data(table='basket', where=2, operand1='user_id', operand2=user_id,
                                      operand3='product_id', operand4=product_id)
                if len(entries) == 0:
                    product_ikm = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Добавить в корзину',
                                              callback_data=cb.new(id=product[0], action='add_basket_count'))],
                        [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=back_id, action='back'))]
                    ])
                else:
                    product_ikm = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='-', callback_data=cb.new(id=product[0], action='dec_basket_count')),
                         InlineKeyboardButton(text='+', callback_data=cb.new(id=product[0], action='inc_basket_count'))],
                        [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=back_id, action='back'))]
                    ])
                return text, product_ikm, photo
        return ()

    @staticmethod
    def get_basket(user_id: int) -> tuple:
        cb = CallbackData('basket', 'action')
        text = ''
        total_cost = 0
        i = 1
        for entry in db.get_data(table='basket', where=1, operand1='user_id', operand2=user_id):
            name, cost = db.get_data(get_name_product=1, field1='name', field2='cost', operand1=entry[2])[0]
            text += f'<b>{i}.</b> <b>Название</b> {name}; <b>Кол.</b> {entry[3]}; <b>Сумма</b> {cost * entry[3]}₸.' + '\n'
            total_cost += cost * entry[3]
            i += 1
        text += f'<b>К оплате:</b> {total_cost}₸'
        basket_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Оформить заказ', callback_data=cb.new(action='place_an_order'))],
            [InlineKeyboardButton(text='Редактировать корзину', callback_data=cb.new(action='edit_basket'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, basket_ikm

    @staticmethod
    def get_edit_basket(user_id: int) -> tuple:
        cb = CallbackData('edit_basket', 'id', 'action')
        basket_edit = db.get_data(table='basket', where=1, operand1='user_id', operand2=user_id)
        if len(basket_edit) <= 24:
            basket_edit_ikm = InlineKeyboardMarkup(row_width=4)
            buttons = []
            text = f'Редактирование корзины. Всего товаров: {len(basket_edit)}'
            for entry in basket_edit:
                name = db.get_data(get_name_product=1, field1='name', operand1=entry[2])[0][0]
                buttons.append(InlineKeyboardButton(text='-', callback_data=cb.new(id=entry[2], action='dec')))
                buttons.append(InlineKeyboardButton(text=name, callback_data=cb.new(id=entry[2], action='open_product')))
                buttons.append(InlineKeyboardButton(text='+', callback_data=cb.new(id=entry[2], action='inc')))
                buttons.append(InlineKeyboardButton(text=str(entry[3]), callback_data=cb.new(id=-1, action='')))
            buttons.append(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
            basket_edit_ikm.add(*buttons)
            return text, basket_edit_ikm
