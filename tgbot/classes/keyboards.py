from datetime import datetime
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
    def get_balance_user(user_id: int) -> tuple:
        db.check_user(user_id=user_id)
        text = f"Ваш баланс: {db.get_data(table='users', where=1, operand1='id', operand2=user_id)[0][1]}₸"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data='delete_balance_message')]
        ])
        return text, keyboard

    @staticmethod
    def add_balance_user(user_id: int) -> tuple:
        db.check_user(user_id=user_id)
        db.add_balance(user_id=user_id)
        text = f"Ваш баланс пополнен на 10000₸"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data='delete_balance_message')]
        ])
        return text, keyboard

    @staticmethod
    def set_address_user(**kwargs) -> tuple:
        db.check_user(user_id=kwargs['user_id'])
        if kwargs['pos'] == 0:
            text = f'Укажите актуальный адрес доставки следуюищим сообщением:'
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Понятно', callback_data='delete_balance_message')]
            ])
        else:
            db.update_address(user_id=kwargs['user_id'], address=kwargs['address'])
            text = f"Адрес: {kwargs['address']} утвреждён"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Понятно', callback_data='delete_balance_message')]
            ])
        return text, keyboard

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
                buttons.append(InlineKeyboardButton(text=subcategory[2], callback_data=cb.new(id=subcategory[0], action='subcategory')))
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

    @staticmethod
    def place_an_order(user_id: int) -> str:
        if len(db.get_data(table='basket', where=1, operand1='user_id', operand2=user_id)) > 0:
            int_current_datetime = datetime.now().strftime("%Y%m%d%H%M")
            db.working_with_place_an_order(insert_in_orders=1, date=int_current_datetime)
            order_id = db.get_data(table='orders', where=1, operand1='reg_date', operand2=int_current_datetime)[0][0]
            for entry in db.get_data(table='basket', where=1, operand1='user_id', operand2=user_id):
                cost = db.get_data(table='products', where=1, operand1='id', operand2=entry[2])[0][6]
                db.working_with_place_an_order(insert_in_order_items=1, order_id=order_id, user_id=user_id, product_id=entry[2], count=entry[3], cost=cost)
            text = 'Заказ успешно оформлен!' + '\n'
            db.working_with_place_an_order(clear_basket=1, user_id=user_id)
            text += 'Корзина очищена!'
        else:
            text = 'Корзина пуста! Сначало добавьте товар!'
        return text

    @staticmethod
    def get_orders(user_id: int) -> InlineKeyboardMarkup:
        cb = CallbackData('orders', 'id', 'action')
        orders_ikm = InlineKeyboardMarkup(row_width=3)
        buttons = []
        for entry in db.get_data(table='order_items', where=1, operand1='user_id', operand2=user_id):
            reg_date = str(db.get_data(table='orders', where=1, operand1='id', operand2=entry[1])[0][1])
            res_date = reg_date[6:8] + '.' + reg_date[4:6] + '.' + reg_date[0:4] + ' ' + reg_date[8:10] + ':' + reg_date[10:12]
            buttons.append(InlineKeyboardButton(text=f'{res_date}', callback_data=cb.new(id=entry[1], action='order_item')))
            if db.get_data(table='orders', where=1, operand1='id', operand2=entry[1])[0][2] == 0:
                buttons.append(InlineKeyboardButton(text='Не оплачен', callback_data=cb.new(id=-2, action='is_paid')))
            else:
                buttons.append(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='is_paid')))
            if db.get_data(table='orders', where=1, operand1='id', operand2=entry[1])[0][3] == 0:
                buttons.append(InlineKeyboardButton(text='Не доставлен', callback_data=cb.new(id=-2, action='is_delivered')))
            else:
                buttons.append(InlineKeyboardButton(text='Доставлен', callback_data=cb.new(id=-2, action='is_delivered')))
        buttons.append(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        orders_ikm.add(*buttons)
        return orders_ikm

    @staticmethod
    def get_order_item(order_id: int) -> tuple:
        cb = CallbackData('order_item', 'id', 'action')
        order = db.get_data(table='orders', where=1, operand1='id', operand2=order_id)
        total_cost = 0
        text = ''
        i = 1
        for entry in db.get_data(table='order_items', where=1, operand1='order_id', operand2=order_id):
            name = db.get_data(get_name_product=1, field1='name', operand1=entry[3])[0]
            text += f'<b>{i}.</b> <b>Название</b> {name}; <b>Кол.</b> {entry[4]}; <b>Стоимость</b> {entry[5]}₸.' + '\n'
            total_cost += entry[5] * entry[4]
            i += 1
        text += f'<b>К оплате:</b> {total_cost}₸'
        order_item_ikm = InlineKeyboardMarkup(row_width=1)
        if order[0][2] == 0:
            order_item_ikm.add(InlineKeyboardButton(text='Оплатить', callback_data=cb.new(id=order_id, action='to_pay')))
        else:
            order_item_ikm.add(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='paid_for')))
            if order[0][3] == 0:
                order_item_ikm.add(InlineKeyboardButton(text='Не доставлен', callback_data=cb.new(id=-3, action='not_delivered')))
            else:
                order_item_ikm.add(InlineKeyboardButton(text='Доставлен', callback_data=cb.new(id=-3, action='delivered')))
        order_item_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, order_item_ikm

    @staticmethod
    def get_total_cost(order_id: int) -> int:
        total_cost = 0
        for entry in db.get_data(table='order_items', where=1, operand1='order_id', operand2=order_id):
            total_cost += entry[5] * entry[4]
        return total_cost

