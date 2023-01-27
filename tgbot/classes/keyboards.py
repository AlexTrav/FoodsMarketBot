import random
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from tgbot.db.database import db
from tgbot.variables.config import Documents

class Keyboards:


#######################################################################USER#########################################################################################

    @staticmethod
    def get_start_ikm() -> InlineKeyboardMarkup:
        start_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Каталог продуктов', callback_data='product_catalog')],
            [InlineKeyboardButton(text='Моя корзина', callback_data='my_basket')],
            [InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')],
            [InlineKeyboardButton(text='Глобальный поиск', callback_data='search')],
            [InlineKeyboardButton(text='Профиль', callback_data='profile')],
            [InlineKeyboardButton(text='Работа', callback_data='work')]
        ])
        return start_ikm

    @staticmethod
    def get_balance_user(user_id: int) -> tuple:
        cb = CallbackData('del_message', 'action')
        db.check_user(user_id=user_id)
        text = f"Ваш баланс: {db.get_data(table='users', where=1, operand1='id', operand2=user_id)[0][1]}₸"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, keyboard

    @staticmethod
    def add_balance_user(user_id: int) -> str:
        db.check_user(user_id=user_id)
        db.add_balance(user_id=user_id)
        text = f"Ваш баланс пополнен на 10000₸"
        return text

    @staticmethod
    def set_address_user(**kwargs) -> tuple:
        db.check_user(user_id=kwargs['user_id'])
        cb = CallbackData('del_message', 'action')
        if kwargs['pos'] == 0:
            text = f'Укажите актуальный адрес доставки следуюищим сообщением:'
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
            ])
            return text, keyboard
        else:
            db.update_address(user_id=kwargs['user_id'], address=kwargs['address'])

    @staticmethod
    def set_phone_user(**kwargs) -> tuple:
        db.check_user(user_id=kwargs['user_id'])
        cb = CallbackData('del_message', 'action')
        if kwargs['pos'] == 0:
            text = f'Укажите актуальный номер мобильного телефона:'
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
            ])
            return text, keyboard
        else:
            db.update_phone(user_id=kwargs['user_id'], phone=kwargs['phone'])

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
                if product[8] > 0:
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
            db.working_with_place_an_order(insert_in_orders=1, date=int_current_datetime, user_id=user_id)
            order_id = db.get_data(table='orders', where=1, operand1='reg_date', operand2=int_current_datetime)[0][0]
            total_cost = 0
            text = ''
            for entry in db.get_data(table='basket', where=1, operand1='user_id', operand2=user_id):
                count_stock = db.get_data(get_name_product=1, field1='count', operand1=entry[2])[0][0]
                if entry[3] > count_stock:
                    text = f'Количество товаров изменено! '
                    db.update_count_basket(basket_id=entry[0], count_stock=count_stock)
            for entry in db.get_data(table='basket', where=1, operand1='user_id', operand2=user_id):
                name, cost = db.get_data(get_name_product=1, field1='name', field2='cost', operand1=entry[2])[0]
                total_cost += cost * entry[3]
                db.working_with_place_an_order(insert_in_order_items=1, order_id=order_id, user_id=user_id, product_id=entry[2], count=entry[3], cost=cost)
            db.working_with_place_an_order(insert_in_orders_total_cost=1, total_cost=total_cost, user_id=user_id, order_id=order_id)
            text += 'Заказ успешно оформлен! '
            db.update_count_product(user_id=user_id)
            db.working_with_place_an_order(clear_basket=1, user_id=user_id)
            text += 'Корзина очищена!'
        else:
            text = 'Корзина пуста! Сначало добавьте товар!'
        return text

    @staticmethod
    def get_orders(user_id: int) -> InlineKeyboardMarkup:
        orders = db.get_data(table='orders', where=1, operand1='user_id', operand2=user_id)
        if len(orders) <= 33:
            cb = CallbackData('orders', 'id', 'action')
            orders_ikm = InlineKeyboardMarkup(row_width=3)
            buttons = []
            for entry in orders:
                res_date = str(entry[2])[6:8] + '.' + str(entry[2])[4:6] + ' ' + str(entry[2])[8:10] + ':' + str(entry[2])[10:12]
                buttons.append(InlineKeyboardButton(text=f'{res_date}', callback_data=cb.new(id=entry[0], action='order_item')))
                if entry[3] == 0:
                    buttons.append(InlineKeyboardButton(text='Не оплачен', callback_data=cb.new(id=-2, action='is_paid')))
                else:
                    buttons.append(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='is_paid')))
                if entry[4] == 0:
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
        if order[0][3] == 0:
            order_item_ikm.add(InlineKeyboardButton(text='Оплатить', callback_data=cb.new(id=order_id, action='to_pay')))
        else:
            order_item_ikm.add(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='paid_for')))
            if order[0][4] == 0:
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

    @staticmethod
    def get_profile(user_id: int) -> tuple:
        cb = CallbackData('user_profile', 'action')
        user = db.get_data(table='users', where=1, operand1='id', operand2=user_id)[0]
        my_profile_ikm = InlineKeyboardMarkup(row_width=1)
        text = f'<b>Ваш баланс</b>: {user[1]}₸' + '\n'
        my_profile_ikm.add(InlineKeyboardButton(text='Пополнить баланс', callback_data=cb.new(action='add_balance')))
        if user[2] is None:
            text += f'<b>Ваш адрес</b>: Не указан' + '\n'
            my_profile_ikm.add(InlineKeyboardButton(text='Указать адрес', callback_data=cb.new(action='set_address')))
        else:
            text += f'<b>Ваш адрес</b>: {user[2]}' + '\n'
            my_profile_ikm.add(InlineKeyboardButton(text='Изменить адрес', callback_data=cb.new(action='update_address')))
        if user[3] is None:
            text += f'<b>Ваш телефон</b>: Не указан' + '\n'
            my_profile_ikm.add(InlineKeyboardButton(text='Указать телефон', callback_data=cb.new(action='set_phone')))
        else:
            text += f'<b>Ваш телефон</b>: {user[3]}' + '\n'
            my_profile_ikm.add(InlineKeyboardButton(text='Изменить телефон', callback_data=cb.new(action='update_phone')))
        my_profile_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back')))
        return text, my_profile_ikm

    @staticmethod
    def get_work() -> tuple:
        cb = CallbackData('work', 'action')
        text = 'Добро пожаловать в модуль работы!' + '\n'
        text += 'Выберите одно из предложенных действий'
        work_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Войти как админ', callback_data=cb.new(action='admin'))],
            [InlineKeyboardButton(text='Войти как оператор', callback_data=cb.new(action='operator'))],
            [InlineKeyboardButton(text='Войти как курьер', callback_data=cb.new(action='courier'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, work_ikm

    @staticmethod
    def get_search() -> tuple:
        cb = CallbackData('back', 'action')
        text = 'Введите поисковый запрос (следующим сообщением):'
        search_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, search_ikm


    @staticmethod
    def get_search_products(search_query: str) -> tuple:
        cb = CallbackData('search_answer', 'id', 'action')
        search_products = db.get_search_answer(search_query=search_query)
        if len(search_products) > 0:
            if len(search_products) >= 60:
                text = 'Найдено 60 записей:'
            else:
                text = f'Найдено {len(search_products)} записей:'
            search_answer_ikm = InlineKeyboardMarkup(row_width=3)
            buttons = []
            for product in search_products:
                if len(buttons) == 60:
                    break
                buttons.append(InlineKeyboardButton(text=product[2], callback_data=cb.new(id=product[0], action='search_product')))
            search_answer_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        else:
            text = 'К сожалению записей не найдено'
            search_answer_ikm = InlineKeyboardMarkup(row_width=3, inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
        return text, search_answer_ikm

#######################################################################ADMIN#######################################################################################


#######################################################################OPERATOR####################################################################################

    @staticmethod
    def get_start_operator() -> InlineKeyboardMarkup:
        start_operator_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Работа со складом', callback_data='products')],
            [InlineKeyboardButton(text='Выйти', callback_data='exit')]
        ])
        return start_operator_ikm

    @staticmethod
    def get_working_warehouse() -> tuple:
        cb = CallbackData('working_warehouse', 'action')
        working_warehouse_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить товар', callback_data=cb.new(action='add_product'))],
            [InlineKeyboardButton(text='Поиск по коду', callback_data=cb.new(action='search_id'))],
            [InlineKeyboardButton(text='Глобальный поиск', callback_data=cb.new(action='search'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        text = 'Выберите одно из действий:'
        return text, working_warehouse_ikm

    @staticmethod
    def get_product_operator(product_id: int) -> tuple:
        cb = CallbackData('product', 'id', 'action')
        for product in db.get_data(table='products'):
            if product[0] == int(product_id):
                text = f'Код товара: {product[0]} \n'
                text += f'Название: {product[2]}. \n'
                if product[3] != '':
                    text += f'Производитель: {product[3]}. \n'
                if product[4] != '':
                    text += f'Брэнд: {product[4]}. \n'
                if product[5] != '':
                    text += f'Описание: {product[5]} \n'
                text += f'Цена: {product[6]}₸. \n'
                text += f'Количество на складе: {product[8]}. \n'
                photo = product[7]
                text += f'Добавленное количество: {Documents.new_count}. \n'
                if Documents.new_price.isdigit():
                    text += f'Новая цена: {Documents.new_price}₸. \n'
                else:
                    text += f'Новая цена: \n'
                product_ikm = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Сохранить', callback_data=cb.new(id=product[0], action='save'))],
                    [InlineKeyboardButton(text='-', callback_data=cb.new(id=product[0], action='dec_count_product')),
                     InlineKeyboardButton(text=Documents.new_count, callback_data=cb.new(id=0, action='count_product')),
                     InlineKeyboardButton(text='+', callback_data=cb.new(id=product[0], action='inc_count_product'))],
                    [InlineKeyboardButton(text='Изменить цену', callback_data=cb.new(id=product[0], action='change_price'))],
                    [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
                ])
                return text, product_ikm, photo
        return ()

    @staticmethod
    def get_answer_operator(state: str) -> str:
        answer = ''
        if state == 'dec_count_product':
            if Documents.new_count == 0:
                answer = 'Добавленное количество не может быть меньше 0'
            else:
                Documents.new_count -= 1
                answer = 'Количетсво уменьшено на 1'
        elif state == 'inc_count_product':
            Documents.new_count += 1
            answer = 'Количетсво увеличено на 1'
        return answer


    @staticmethod
    def get_change_price_product() -> tuple:
        cb = CallbackData('change_price', 'action')
        text = 'Введите новую цену (следующим сообщением):'
        search_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, search_ikm

    @staticmethod
    def set_new_price(new_price: int) -> None:
        Documents.new_price = new_price


    @staticmethod
    def saving_the_operator_work(product_id: int, user_id: int) -> str:
        if Documents.new_count == 0 and Documents.new_price == '':
            return 'Чтобы сохранить, измените что нибудь!'
        invoice_number = random.randint(1000000, 9999999)
        invoice_date = datetime.now().strftime("%Y%m%d%H%M")
        if Documents.new_price.isdigit():
            cost = Documents.new_price
            db.product_change_price(new_price=Documents.new_price, product_id=product_id)
        else:
            cost = db.get_data(get_name_product=1, field1='cost', operand1=product_id)[0][0]
        db.product_change_count(new_count=Documents.new_count, product_id=product_id)
        db.insert_documents(user_id=user_id, product_id=product_id, invoice_date=invoice_date, count=Documents.new_count, cost=cost, invoice_number=invoice_number)
        Documents.new_count = 0
        Documents.new_price = ''
        return 'Успешно'

    @staticmethod
    def get_search_id() -> tuple:
        cb = CallbackData('back', 'action')
        text = 'Введите код товара (следующим сообщением):'
        search_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, search_ikm

    @staticmethod
    def get_search_id_product(search_id: int) -> tuple:
        cb = CallbackData('search_answer', 'id', 'action')
        search_product = db.get_data(table='products', where=1, operand1='id', operand2=search_id)
        if len(search_product) > 0:
            text = 'Запись найдена!'
            search_answer_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
                [InlineKeyboardButton(text=search_product[0][2], callback_data=cb.new(id=search_id, action='search_product'))],
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
        else:
            text = 'К сожалению запись не найдена'
            search_answer_ikm = InlineKeyboardMarkup(row_width=3, inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
        return text, search_answer_ikm

#######################################################################COURIER#####################################################################################

    @staticmethod
    def get_start_courier() -> InlineKeyboardMarkup:
        start_courier_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Заказы', callback_data='orders')],
            [InlineKeyboardButton(text='Выйти', callback_data='exit')]
        ])
        return start_courier_ikm

    @staticmethod
    def get_undelivered_orders() -> tuple:
        cb = CallbackData('delivery', 'id', 'action')
        text = 'Недоставленные заказы:'
        delivery_ikm = InlineKeyboardMarkup(row_width=1)
        buttons = []
        for entry in db.get_data(table='delivery', where=1, operand1='is_completed', operand2=0):
            order = db.get_data(table='orders', where=1, operand1='id', operand2=entry[1])[0]
            res_date = str(order[2])[6:8] + '.' + str(order[2])[4:6] + ' ' + str(order[2])[8:10] + ':' + str(order[2])[10:12]
            buttons.append(InlineKeyboardButton(text=f'{res_date}', callback_data=cb.new(id=entry[1], action='order_item')))
        buttons.append(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        delivery_ikm.add(*buttons)
        return text, delivery_ikm

    @staticmethod
    def get_order_item_courier(order_id: int) -> tuple:
        cb = CallbackData('order_item', 'id', 'action')
        order = db.get_data(table='orders', where=1, operand1='id', operand2=order_id)[0]
        user = db.get_data(table='users', where=1, operand1='id', operand2=order[1])[0]
        text = f'<b>Заказ под номером</b> {order_id}, <b>для пользователя</b>: {order[1]}.' + '\n'
        text += f'<b>Состовляющие заказа:</b>' + '\n'
        i = 1
        for entry in db.get_data(table='order_items', where=1, operand1='order_id', operand2=order_id):
            name = db.get_data(get_name_product=1, field1='name', operand1=entry[3])[0]
            text += f'<b>{i}.</b> <b>Название</b> {name}; <b>Кол.</b> {entry[4]}; <b>Стоимость</b> {entry[5]}₸.' + '\n'
            i += 1
        text += f'<b>Сумма заказа:</b> {order[5]}₸.' + '\n'
        text += '<b>Состовляющие пользователя:</b>' + '\n'
        text += f'<b>Адрес доставки:</b> {user[2]}.' + '\n'
        text += f'<b>Номер телефона:</b> {user[3]}.'
        delivery_order_item_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Доставил', callback_data=cb.new(id=order[0], action='delivered'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
        ])
        return text, delivery_order_item_ikm
