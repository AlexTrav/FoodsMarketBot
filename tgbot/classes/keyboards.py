import random
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from tgbot.db.database import db
from tgbot.variables.config import Documents, Products, Users, MainPage


class Keyboards:

#######################################################################USER#########################################################################################

    @staticmethod
    def get_start_ikm(user_id: int) -> InlineKeyboardMarkup:
        start_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Каталог продуктов', callback_data='product_catalog')],
            [InlineKeyboardButton(text='Моя корзина', callback_data='my_basket')],
            [InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')],
            [InlineKeyboardButton(text='Глобальный поиск', callback_data='search')],
            [InlineKeyboardButton(text='Профиль', callback_data='profile')]
        ])
        if user_id in Keyboards.get_workers():
            start_ikm.add(InlineKeyboardButton(text='Работа', callback_data='work'))
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
        if not db.get_document_user(user_id=user_id):
            invoice_number = random.randint(1000000, 9999999)
            invoice_date = datetime.now().strftime("%Y%m%d%H%M")
            db.check_user(user_id=user_id)
            db.add_balance(user_id=user_id, invoice_date=invoice_date, invoice_number=invoice_number)
            text = f"Запрос на пополнение баланса, отправлен. С вами свяжится админ!"
        else:
            text = f"Запрос на пополнение баланса уже есть! Ожидайте!"
        return text

    @staticmethod
    def set_address_user(**kwargs) -> None:
        db.update_address(user_id=kwargs['user_id'], address=kwargs['address'])

    @staticmethod
    def get_location_user_form() -> tuple:
        text = f'Пожалуйста, поделитесь своим местоположением при помощи кнопки снизу'
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(text='Отправить мою геолокацию', request_location=True))
        keyboard.add(KeyboardButton(text='Отмена'))
        return text, keyboard

    @staticmethod
    def set_phone_user(user_id: int, phone_number: str) -> None:
        db.update_phone(user_id=user_id, phone=phone_number)

    @staticmethod
    def get_phone_user_form() -> tuple:
        text = f'Пожалуйста, поделитесь своим номером телефона при помощи кнопки снизу'
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(text='Отправить мой номер телефона', request_contact=True))
        keyboard.add(KeyboardButton(text='Отмена'))
        return text, keyboard

    @staticmethod
    def get_product_catalog() -> InlineKeyboardMarkup:
        cb = CallbackData('categories', 'id', 'action')
        product_catalog_ikm = InlineKeyboardMarkup(row_width=2)
        buttons = []
        for category in db.get_data(table='categories_products'):
            buttons.append(
                InlineKeyboardButton(text=category[1], callback_data=cb.new(id=category[0], action='category')))
        product_catalog_ikm.add(*buttons).add(
            InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return product_catalog_ikm

    @staticmethod
    def get_product_subcatalog(category_id: int) -> InlineKeyboardMarkup:
        cb = CallbackData('subcategories', 'id', 'action')
        product_subcatalog_ikm = InlineKeyboardMarkup(row_width=2)
        buttons = []
        for subcategory in db.get_data(table='subcategories_products'):
            if subcategory[1] == int(category_id):
                buttons.append(InlineKeyboardButton(text=subcategory[2],
                                                    callback_data=cb.new(id=subcategory[0], action='subcategory')))
        product_subcatalog_ikm.add(*buttons).add(
            InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return product_subcatalog_ikm

    @staticmethod
    def get_products(subcategory_id: int) -> InlineKeyboardMarkup:
        cb = CallbackData('products', 'id', 'action')
        products_ikm = InlineKeyboardMarkup(row_width=1)
        buttons = []
        products = db.get_products(subcategory_id=subcategory_id, state=Products.sorting)
        if len(products) > 10:
            if MainPage.entries != 10:
                products_ikm.add(
                    InlineKeyboardButton(text='↑', callback_data=cb.new(id=subcategory_id, action='up_page')))
            for product in products[MainPage.entries - 10:MainPage.entries]:
                if product[8] > 0:
                    buttons.append(
                        InlineKeyboardButton(text=product[2], callback_data=cb.new(id=product[0], action='products')))
            products_ikm.add(*buttons)
            if MainPage.entries < len(products):
                products_ikm.add(
                    InlineKeyboardButton(text='↓', callback_data=cb.new(id=subcategory_id, action='down_page')))
        else:
            for product in products:
                if product[8] > 0:
                    buttons.append(
                        InlineKeyboardButton(text=product[2], callback_data=cb.new(id=product[0], action='products')))
            products_ikm.add(*buttons)
        products_ikm.add(
            InlineKeyboardButton(text='Сортировка', callback_data=cb.new(id=subcategory_id, action='sorting')))
        products_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return products_ikm

    @staticmethod
    def get_sorting_form(subcategory_id: int) -> tuple:
        cb = CallbackData('sorting', 'id', 'action')
        sorting_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='По умолчанию', callback_data=cb.new(id=subcategory_id, action='default'))],
            [InlineKeyboardButton(text='По возрастанию цены',
                                  callback_data=cb.new(id=subcategory_id, action='cost_asc'))],
            [InlineKeyboardButton(text='По убыванию цены',
                                  callback_data=cb.new(id=subcategory_id, action='cost_desc'))],
            {InlineKeyboardButton(text='По наименованию', callback_data=cb.new(id=subcategory_id, action='name'))},
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=subcategory_id, action='back'))]
        ])
        text = 'Выберите сортировку:'
        return text, sorting_ikm

    @staticmethod
    def get_sorting(state: str) -> str:
        if state == 'default':
            if Products.sorting == '':
                answer = 'Сортировка по умолчанию уже выбрана!'
            else:
                Products.sorting = ''
                answer = 'Выбрана сортировка по умолчанию!'
        elif state == 'cost_asc':
            if Products.sorting == 'ORDER BY cost ASC':
                answer = 'Сортировка по возрастанию цены уже выбрана!'
            else:
                Products.sorting = 'ORDER BY cost ASC'
                answer = 'Выбрана сортировка по возрастанию!'
        elif state == 'cost_desc':
            if Products.sorting == 'ORDER BY cost DESC':
                answer = 'Сортировка по убыванию цены уже выбрана!'
            else:
                Products.sorting = 'ORDER BY cost DESC'
                answer = 'Выбрана сортировка по убыванию цены!'
        else:
            if Products.sorting == 'ORDER BY name':
                answer = 'Сортировка по наименованию уже выбрана!'
            else:
                Products.sorting = 'ORDER BY name'
                answer = 'Выбрана сортировка по наименованию!'
        return answer

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
                         InlineKeyboardButton(text='+',
                                              callback_data=cb.new(id=product[0], action='inc_basket_count'))],
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
                buttons.append(
                    InlineKeyboardButton(text=name, callback_data=cb.new(id=entry[2], action='open_product')))
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
                db.working_with_place_an_order(insert_in_order_items=1, order_id=order_id, user_id=user_id,
                                               product_id=entry[2], count=entry[3], cost=cost)
            db.working_with_place_an_order(insert_in_orders_total_cost=1, total_cost=total_cost, user_id=user_id,
                                           order_id=order_id)
            text += 'Заказ успешно оформлен! '
            db.update_count_product(user_id=user_id)
            db.working_with_place_an_order(clear_basket=1, user_id=user_id)
            text += 'Корзина очищена!'
        else:
            text = 'Корзина пуста! Сначало добавьте товар!'
        return text

    @staticmethod
    def get_orders(user_id: int) -> InlineKeyboardMarkup:
        orders = db.get_data(table='orders', where=1, order_by=1, operand1='user_id', operand2=user_id, operand3='id')
        cb = CallbackData('orders', 'id', 'action')
        orders_ikm = InlineKeyboardMarkup(row_width=3)
        buttons = []
        if len(orders) > 10:
            if MainPage.entries != 10:
                orders_ikm.add(InlineKeyboardButton(text='↑', callback_data=cb.new(id=user_id, action='up_page')))
            for entry in orders[MainPage.entries - 10:MainPage.entries]:
                res_date = str(entry[2])[6:8] + '.' + str(entry[2])[4:6] + ' ' + str(entry[2])[8:10] + ':' + str(
                    entry[2])[10:12]
                buttons.append(
                    InlineKeyboardButton(text=f'{res_date}', callback_data=cb.new(id=entry[0], action='order_item')))
                if entry[3] == 0:
                    buttons.append(
                        InlineKeyboardButton(text='Не оплачен', callback_data=cb.new(id=-2, action='is_paid')))
                else:
                    buttons.append(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='is_paid')))
                if entry[4] == 0:
                    buttons.append(
                        InlineKeyboardButton(text='Не доставлен', callback_data=cb.new(id=-2, action='is_delivered')))
                else:
                    buttons.append(
                        InlineKeyboardButton(text='Доставлен', callback_data=cb.new(id=-2, action='is_delivered')))
            orders_ikm.add(*buttons)
            if MainPage.entries < len(orders):
                orders_ikm.add(InlineKeyboardButton(text='↓', callback_data=cb.new(id=user_id, action='down_page')))
        else:
            for entry in orders:
                res_date = str(entry[2])[6:8] + '.' + str(entry[2])[4:6] + ' ' + str(entry[2])[8:10] + ':' + str(
                    entry[2])[10:12]
                buttons.append(
                    InlineKeyboardButton(text=f'{res_date}', callback_data=cb.new(id=entry[0], action='order_item')))
                if entry[3] == 0:
                    buttons.append(
                        InlineKeyboardButton(text='Не оплачен', callback_data=cb.new(id=-2, action='is_paid')))
                else:
                    buttons.append(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='is_paid')))
                if entry[4] == 0:
                    buttons.append(
                        InlineKeyboardButton(text='Не доставлен', callback_data=cb.new(id=-2, action='is_delivered')))
                else:
                    buttons.append(
                        InlineKeyboardButton(text='Доставлен', callback_data=cb.new(id=-2, action='is_delivered')))
            orders_ikm.add(*buttons)
        orders_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return orders_ikm

    @staticmethod
    def get_order_item(order_id: int) -> tuple:
        cb = CallbackData('order_item', 'id', 'action')
        order = db.get_data(table='orders', where=1, operand1='id', operand2=order_id)
        total_cost = 0
        text = f'<b>Заказ под номером:</b> {order_id}' + '\n'
        i = 1
        for entry in db.get_data(table='order_items', where=1, operand1='order_id', operand2=order_id):
            name = db.get_data(get_name_product=1, field1='name', operand1=entry[3])[0]
            text += f'<b>{i}.</b> <b>Название</b> {name}; <b>Кол.</b> {entry[4]}; <b>Стоимость</b> {entry[5]}₸.' + '\n'
            total_cost += entry[5] * entry[4]
            i += 1
        text += f'<b>Общая стоимость заказа:</b> {total_cost}₸'
        order_item_ikm = InlineKeyboardMarkup(row_width=1)
        if order[0][3] == 0:
            order_item_ikm.add(
                InlineKeyboardButton(text='Оплатить', callback_data=cb.new(id=order_id, action='to_pay')))
        else:
            order_item_ikm.add(InlineKeyboardButton(text='Оплачен', callback_data=cb.new(id=-2, action='paid_for')))
            if order[0][4] == 0:
                order_item_ikm.add(
                    InlineKeyboardButton(text='Не доставлен', callback_data=cb.new(id=-3, action='not_delivered')))
            else:
                order_item_ikm.add(
                    InlineKeyboardButton(text='Доставлен', callback_data=cb.new(id=-3, action='delivered')))
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
        if user[2] is None or not user[2]:
            text += f'<b>Ваш адрес</b>: Не указан' + '\n'
            my_profile_ikm.add(
                InlineKeyboardButton(text='Указать местоположение', callback_data=cb.new(action='set_location')))
        else:
            text += f'<b>Ваш адрес</b>: {user[2]}' + '\n'
            my_profile_ikm.add(
                InlineKeyboardButton(text='Изменить местоположение', callback_data=cb.new(action='update_location')))
        if user[3] is None or not user[3]:
            text += f'<b>Ваш телефон</b>: Не указан' + '\n'
            my_profile_ikm.add(InlineKeyboardButton(text='Указать телефон', callback_data=cb.new(action='set_phone')))
        else:
            text += f'<b>Ваш телефон</b>: {user[3]}' + '\n'
        my_profile_ikm.add(InlineKeyboardButton(text='Список менеджеров', callback_data=cb.new(action='list_admins')))
        my_profile_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back')))
        return text, my_profile_ikm

    @staticmethod
    def get_list_admins(user_id: int) -> tuple:
        cb = CallbackData('list_admins', 'id', 'action')
        text = 'Список менеджеров:'
        list_admins_id = db.get_data(table='workers', where=1, operand1='role_id', operand2=4)
        list_admins_ikm = InlineKeyboardMarkup(row_width=3)
        buttons = []
        if len(list_admins_id) > 10:
            if MainPage.entries != 10:
                list_admins_ikm.add(InlineKeyboardButton(text='↑', callback_data=cb.new(id=user_id, action='up_page')))
            for entry in list_admins_id[MainPage.entries - 10:MainPage.entries]:
                user = db.get_data(table='users', where=1, operand1='id', operand2=entry[0])[0]
                link = f"https://t.me/{user[5]}"
                list_admins_ikm.add(InlineKeyboardButton(text=user[5], url=link))
            list_admins_ikm.add(*buttons)
            if MainPage.entries < len(list_admins_id):
                list_admins_ikm.add(
                    InlineKeyboardButton(text='↓', callback_data=cb.new(id=user_id, action='down_page')))
        else:
            for entry in list_admins_id:
                user = db.get_data(table='users', where=1, operand1='id', operand2=entry[0])[0]
                link = f"https://t.me/{user[5]}"
                list_admins_ikm.add(InlineKeyboardButton(text=user[5], url=link))
            list_admins_ikm.add(*buttons)
        list_admins_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, list_admins_ikm

    @staticmethod
    def get_work() -> tuple:
        cb = CallbackData('work', 'action')
        text = 'Добро пожаловать в модуль работы!' + '\n'
        text += 'Выберите одно из предложенных действий:'
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
            text = f'Найдено {len(search_products)} записей:'
            search_answer_ikm = InlineKeyboardMarkup(row_width=1)
            buttons = []
            if len(search_products) > 10:
                if MainPage.entries != 10:
                    search_answer_ikm.add(
                        InlineKeyboardButton(text='↑', callback_data=cb.new(id=search_query, action='up_page')))
                for product in search_products[MainPage.entries - 10:MainPage.entries]:
                    if len(buttons) == 60:
                        break
                    buttons.append(InlineKeyboardButton(text=product[2],
                                                        callback_data=cb.new(id=product[0], action='search_product')))
                search_answer_ikm.add(*buttons)
                if MainPage.entries < len(search_products):
                    search_answer_ikm.add(
                        InlineKeyboardButton(text='↓', callback_data=cb.new(id=search_query, action='down_page')))
            else:
                for product in search_products:
                    if len(buttons) == 60:
                        break
                    buttons.append(InlineKeyboardButton(text=product[2],
                                                        callback_data=cb.new(id=product[0], action='search_product')))
                search_answer_ikm.add(*buttons)
            search_answer_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        else:
            text = 'К сожалению записей не найдено'
            search_answer_ikm = InlineKeyboardMarkup(row_width=3, inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
        return text, search_answer_ikm

    @staticmethod
    def get_workers() -> list:
        workers_ids = []
        for entry in db.get_data(table='workers'):
            workers_ids.append(entry[0])
        return workers_ids

    @staticmethod
    def get_users_table() -> list:
        users_ids = []
        for entry in db.get_data(table='users'):
            users_ids.append(entry[0])
        return users_ids

    @staticmethod
    def get_usernames() -> list:
        usernames = []
        for entry in db.get_data(table='users'):
            usernames.append(entry[5])
        return usernames

    @staticmethod
    def get_user_id_for_username(username: str) -> int:
        user_id = int(db.get_data(table='users', where=1, operand1='user_name', operand2=username)[0][0])
        return user_id

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
            [InlineKeyboardButton(text='Прибытие товара', callback_data=cb.new(action='arrival_product'))],
            [InlineKeyboardButton(text='Списание товара', callback_data=cb.new(action='write_off_product'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        text = 'Выберите одно из действий:'
        return text, working_warehouse_ikm

    @staticmethod
    def get_search_working_warehouse() -> tuple:
        cb = CallbackData('search_working_warehouse', 'action')
        search_working_warehouse_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Поиск по коду', callback_data=cb.new(action='search_id'))],
            [InlineKeyboardButton(text='Глобальный поиск', callback_data=cb.new(action='search'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        text = 'Выберите одно из действий:'
        return text, search_working_warehouse_ikm

    @staticmethod
    def get_product_operator(product_id: int, state: str) -> tuple:
        product = db.get_data(table='products', where=1, operand1='id', operand2=product_id)[0]
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
        if state == 'arrival_product':
            cb = CallbackData('arrival_product', 'id', 'action')
            text += f'Добавленное количество: {Documents.new_count}. \n'
            if Documents.new_price.isdigit():
                text += f'Новая цена: {Documents.new_price}₸. \n'
            else:
                text += f'Новая цена: \n'
            product_ikm = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Сохранить', callback_data=cb.new(id=product[0], action='save'))],
                [InlineKeyboardButton(text='-', callback_data=cb.new(id=product[0], action='dec_count_product')), InlineKeyboardButton(text=Documents.new_count, callback_data=cb.new(id=0, action='count_product')), InlineKeyboardButton(text='+', callback_data=cb.new(id=product[0], action='inc_count_product'))],
                [InlineKeyboardButton(text='Изменить цену', callback_data=cb.new(id=product[0], action='change_price'))],
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
            return text, product_ikm, photo
        elif state == 'write_off_product':
            cb = CallbackData('write_off_product', 'id', 'action')
            text += f'Количество списанного: {Documents.write_off_count}. \n'
            product_ikm = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='-', callback_data=cb.new(id=product[0], action='dec_count_product')), InlineKeyboardButton(text=Documents.write_off_count, callback_data=cb.new(id=0, action='count_product')), InlineKeyboardButton(text='+', callback_data=cb.new(id=product[0], action='inc_count_product'))],
                [InlineKeyboardButton(text='Списать', callback_data=cb.new(id=product[0], action='write_off'))],
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
            return text, product_ikm, photo

    @staticmethod
    def get_answer_operator_arrival_product(state: str) -> str:
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
    def get_answer_operator_write_off_product(state: str) -> str:
        answer = ''
        if state == 'dec_count_product':
            if Documents.write_off_count == 0:
                answer = 'Количество списанного не может быть меньше 0'
            else:
                Documents.write_off_count -= 1
                answer = 'Количетсво уменьшено на 1'
        elif state == 'inc_count_product':
            Documents.write_off_count += 1
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
        db.product_change_count(new_count=Documents.new_count, product_id=product_id, arrival_product=1)
        db.insert_documents(arrival_product=1, user_id=user_id, product_id=product_id, invoice_date=invoice_date,
                            count=Documents.new_count, cost=cost, invoice_number=invoice_number)
        Documents.new_count = 0
        Documents.new_price = ''
        return 'Успешно'

    @staticmethod
    def write_off_product_work(product_id: int, user_id: int) -> str:
        count_product = db.get_data(get_name_product=1, field1='count', operand1=product_id)[0][0]
        if Documents.write_off_count > count_product:
            return 'Нельзя списать, больше чем есть на складе!'
        if Documents.write_off_count == 0:
            return 'Чтобы списать, измените что нибудь!'
        invoice_number = random.randint(1000000, 9999999)
        invoice_date = datetime.now().strftime("%Y%m%d%H%M")
        cost = db.get_data(get_name_product=1, field1='cost', operand1=product_id)[0][0]
        db.product_change_count(write_off_count=Documents.write_off_count, product_id=product_id, write_off_product=1)
        db.insert_documents(write_off_product=1, user_id=user_id, product_id=product_id, invoice_date=invoice_date,
                            count=Documents.write_off_count, cost=cost, invoice_number=invoice_number)
        Documents.write_off_count = 0
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
                [InlineKeyboardButton(text=search_product[0][2],
                                      callback_data=cb.new(id=search_id, action='search_product'))],
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
        else:
            text = 'К сожалению запись не найдена'
            search_answer_ikm = InlineKeyboardMarkup(row_width=3, inline_keyboard=[
                [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
            ])
        return text, search_answer_ikm

    @staticmethod
    def get_add_product() -> tuple:
        cb = CallbackData('add_product_msg', 'action')
        if Products.subcategory_id:
            subcategory = db.get_subcategory(subcategory_id=Products.subcategory_id)
            text = f'Подкатегория: {subcategory} \n'
        else:
            text = f'Подкатегория: \n'
        text += 'Введите <b>Наименование товара</b>; <b>Страну производителя</b>; <b>Брэнд</b>; <b>Описание</b>; <b>Цену</b>; <b>Фото (ссылкой)</b>. Через <b>;</b>'
        add_product_msg_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Выбрать подкатегорию', callback_data=cb.new(action='select_subcategory'))],
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, add_product_msg_ikm

    @staticmethod
    def add_product(message_product: str) -> str:
        product = message_product.split(';')
        if Products.subcategory_id:
            if product[0]:
                if product[4]:
                    if product[4].isdigit():
                        if product[5]:
                            db.insert_product(subcategory_id=Products.subcategory_id, name=product[0],
                                              producing_country=product[1], brand=product[2], description=product[3],
                                              cost=product[4], photo=product[5])
                            product_id = db.get_id(name=product[0])
                            answer = f'Продукт добавлен! Его код: {product_id}'
                            Products.subcategory_id = ''
                        else:
                            answer = 'У товара должно быть фото!'
                    else:
                        answer = 'Цена должна быть числом!'
                else:
                    answer = 'У товара должна быть цена!'
            else:
                answer = 'У товара должно быть наименование!'
        else:
            answer = 'Подкатегория не выбрана!'
        return answer

    @staticmethod
    def get_answer_subcategory(subcategory_id: int) -> str:
        Products.subcategory_id = int(subcategory_id)
        subcategory_name = db.get_subcategory(subcategory_id=subcategory_id)
        answer = f'Выбрана подкатегория: {subcategory_name}'
        return answer

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
            res_date = str(order[2])[6:8] + '.' + str(order[2])[4:6] + ' ' + str(order[2])[8:10] + ':' + str(order[2])[
                                                                                                         10:12]
            buttons.append(
                InlineKeyboardButton(text=f'{res_date}', callback_data=cb.new(id=entry[1], action='order_item')))
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
        text += f'<b>Номер телефона:</b> {user[3]}.' + '\n'
        delivery_order_item_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Доставил', callback_data=cb.new(id=order[0], action='delivered'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back'))]
        ])
        link = f"https://t.me/{user[5]}"
        text += f'Ссылка на пользователя: {link}.' + '\n'
        return text, delivery_order_item_ikm

    #######################################################################ADMIN#######################################################################################

    @staticmethod
    def get_start_admin() -> InlineKeyboardMarkup:
        start_admin_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Работа со складом', callback_data='products')],
            [InlineKeyboardButton(text='Работа с пользователем', callback_data='users')],  # --> 1. , 2.
            [InlineKeyboardButton(text='Документы', callback_data='documents')],
            # --> 1, 2, 3 ... [InlineKeyboardButton(text='(document_types.name)', callback_data='documents')]
            [InlineKeyboardButton(text='Выйти', callback_data='exit')]
        ])
        return start_admin_ikm

    @staticmethod
    def get_users() -> tuple:
        cb = CallbackData('users', 'action')
        text = 'Выберите действие:'
        get_users_admin_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Выдача прав', callback_data=cb.new(action='give_role'))],
            # [InlineKeyboardButton(text='Пополнение баланса', callback_data=cb.new(action='add_balance'))]
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, get_users_admin_ikm

    @staticmethod
    def get_users_() -> tuple:
        cb = CallbackData('users_', 'id', 'action')
        text = 'Пользователи:'
        get_users_admin_ikm = InlineKeyboardMarkup(row_width=1)
        users = db.get_data(table='users')
        buttons = []
        if len(users) > 10:
            if MainPage.entries != 10:
                get_users_admin_ikm.add(InlineKeyboardButton(text='↑', callback_data=cb.new(id=0, action='up_page')))
            for entry in users[MainPage.entries - 10:MainPage.entries]:
                buttons.append(InlineKeyboardButton(text=entry[5], callback_data=cb.new(id=entry[0], action='user')))
            get_users_admin_ikm.add(*buttons)
            if MainPage.entries < len(users):
                get_users_admin_ikm.add(InlineKeyboardButton(text='↓', callback_data=cb.new(id=0, action='down_page')))
        else:
            for entry in users:
                buttons.append(InlineKeyboardButton(text=entry[5], callback_data=cb.new(id=entry[0], action='user')))
            get_users_admin_ikm.add(*buttons)
        get_users_admin_ikm.add(InlineKeyboardButton(text='Поиск', callback_data=cb.new(id=1, action='search')))
        get_users_admin_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, get_users_admin_ikm

    @staticmethod
    def set_username() -> tuple:
        cb = CallbackData('set_username', 'action')
        text = 'Введите username пользователя (следующим сообщением):'
        set_user_id_ikm = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back'))]
        ])
        return text, set_user_id_ikm

    @staticmethod
    def get_user_roles(user_id: int) -> tuple:
        cb = CallbackData('roles_info', 'id', 'action')
        text = f'Пользователь: {user_id} \n'
        text += 'Роли: \n'
        is_operator, is_courier, is_admin = db.is_roles(user_id=user_id)
        text += f'Опетратор: {"✅" if is_operator else "❌"} \n'
        text += f'Курьер: {"✅" if is_courier else "❌"} \n'
        text += f'Админ: {"✅" if is_admin else "❌"} \n'
        roles_ikm = InlineKeyboardMarkup(row_width=1)
        if is_operator:
            roles_ikm.add(InlineKeyboardButton(text='Убрать роль оператора',
                                               callback_data=cb.new(id=user_id, action='del_role_operator')))
        else:
            roles_ikm.add(InlineKeyboardButton(text='Добавить роль оператора',
                                               callback_data=cb.new(id=user_id, action='add_role_operator')))
        if is_courier:
            roles_ikm.add(InlineKeyboardButton(text='Убрать роль курьера',
                                               callback_data=cb.new(id=user_id, action='del_role_courier')))
        else:
            roles_ikm.add(InlineKeyboardButton(text='Добавить роль курьера',
                                               callback_data=cb.new(id=user_id, action='add_role_courier')))
        if is_admin:
            roles_ikm.add(InlineKeyboardButton(text='Убрать роль админа',
                                               callback_data=cb.new(id=user_id, action='del_role_admin')))
        else:
            roles_ikm.add(InlineKeyboardButton(text='Добавить роль админа',
                                               callback_data=cb.new(id=user_id, action='add_role_admin')))
        roles_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, roles_ikm

    @staticmethod
    def get_user_inf(user_id: int) -> tuple:
        cb = CallbackData('user_info', 'id', 'action')
        user = db.get_data(table='users', where=1, operand1='id', operand2=user_id)[0]
        text = f'Пользователь: {user_id} \n'
        user_profile_ikm = InlineKeyboardMarkup(row_width=1)
        user_profile_ikm.add(
            InlineKeyboardButton(text='Пополнить баланс', callback_data=cb.new(id=user_id, action='add_balance')))
        text += f'<b>Баланс</b>: {user[1]}₸' + '\n'
        if user[2] is None:
            text += f'Адрес: Не указан' + '\n'
        else:
            text += f'Адрес: {user[2]}' + '\n'
        if user[3] is None:
            text += f'Телефон: Не указан' + '\n'
        else:
            text += f'Телефон: {user[3]}' + '\n'
        link = f"https://t.me/{user[5]}"
        text += f'Ссылка на пользователя: {link}'
        user_profile_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, user_profile_ikm

    @staticmethod
    def get_add_balance_form(user_id: int) -> tuple:
        cb = CallbackData('back', 'id', 'action')
        Users.id = user_id
        text = 'Введите сумму на которую хотите пополнить счёт пользователю (следующим сообщением):'
        search_ikm = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text='Понятно', callback_data=cb.new(id=-1, action='delete'))],
            [InlineKeyboardButton(text='Назад', callback_data=cb.new(id=user_id, action='back'))]
        ])
        return text, search_ikm

    @staticmethod
    def get_document_types() -> tuple:
        cb = CallbackData('document_types', 'id', 'action')
        text = 'Выберите тип документа'
        documents_type_ikm = InlineKeyboardMarkup(row_width=1)
        buttons = []
        for entry in db.get_data(table='document_types'):
            buttons.append(InlineKeyboardButton(text=entry[1], callback_data=cb.new(id=entry[0], action='document')))
        documents_type_ikm.add(*buttons).add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, documents_type_ikm

    @staticmethod
    def get_insert_documents_add_balance(admin_user_id: int, add_balance_sum: int) -> None:
        invoice_number = random.randint(1000000, 9999999)
        invoice_date = datetime.now().strftime("%Y%m%d%H%M")
        db.insert_documents_add_balance(admin_user_id=admin_user_id, user_id=Users.id, invoice_date=invoice_date,
                                        add_balance_sum=add_balance_sum, invoice_number=invoice_number)

    @staticmethod
    def get_update_documents_add_balance(admin_user_id: int, add_balance_sum: int, doc_id: int) -> None:
        db.update_documents_add_balance(admin_user_id=admin_user_id, add_balance_sum=add_balance_sum, doc_id=doc_id)

    @staticmethod
    def get_documents(doc_type_id: int) -> tuple:
        cb = CallbackData('document', 'id', 'action')
        text = 'Выберите документ:'
        documents_type_ikm = InlineKeyboardMarkup(row_width=1)
        if doc_type_id == '5':
            documents = db.get_data(table='orders', order_by=1, operand1='id')
        else:
            documents = db.get_data(table='documents', where=1, order_by=1, operand1='doc_type_id', operand2=doc_type_id, operand3='id')
        buttons = []
        if len(documents) > 10:
            if MainPage.entries != 10:
                documents_type_ikm.add(
                    InlineKeyboardButton(text='↑', callback_data=cb.new(id=doc_type_id, action='up_page')))
            for document in documents[MainPage.entries - 10:MainPage.entries]:
                if doc_type_id == '5':
                    res_date = str(document[2])[6:8] + '.' + str(document[2])[4:6] + '.' + str(document[2])[2:4] + ' ' + str(document[2])[8:10] + ':' + str(document[2])[10:12]
                else:
                    res_date = str(document[4])[6:8] + '.' + str(document[4])[4:6] + '.' + str(document[4])[2:4] + ' ' + str(document[4])[8:10] + ':' + str(document[4])[10:12]
                buttons.append(InlineKeyboardButton(text=res_date, callback_data=cb.new(id=document[0], action='document')))
            documents_type_ikm.add(*buttons)
            if MainPage.entries < len(documents):
                documents_type_ikm.add(
                    InlineKeyboardButton(text='↓', callback_data=cb.new(id=doc_type_id, action='down_page')))
        else:
            for document in documents:
                if doc_type_id == '5':
                    res_date = str(document[2])[6:8] + '.' + str(document[2])[4:6] + '.' + str(document[2])[2:4] + ' ' + str(document[2])[8:10] + ':' + str(document[2])[10:12]
                else:
                    res_date = str(document[4])[6:8] + '.' + str(document[4])[4:6] + '.' + str(document[4])[2:4] + ' ' + str(document[4])[8:10] + ':' + str(document[4])[10:12]
                buttons.append(InlineKeyboardButton(text=res_date, callback_data=cb.new(id=document[0], action='document')))
            documents_type_ikm.add(*buttons)
        if doc_type_id == '5':
            documents_type_ikm.add(InlineKeyboardButton(text='Сформировать отчёт', callback_data=cb.new(id=0, action='generate_report')))
        documents_type_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, documents_type_ikm

    @staticmethod
    def get_orders_date():
        cb = CallbackData('date', 'id', 'action')
        text = 'Выберите дату:'
        orders_date_ikm = InlineKeyboardMarkup(row_width=1)
        dates = db.get_orders_dates()
        buttons = []
        if len(dates) > 10:
            if MainPage.entries != 10:
                orders_date_ikm.add(InlineKeyboardButton(text='↑', callback_data=cb.new(id=0, action='up_page')))
            for date in dates[MainPage.entries - 10:MainPage.entries]:
                res_date = str(date)[6:8] + '.' + str(date)[4:6] + '.' + str(date)[2:4]
                buttons.append(InlineKeyboardButton(text=res_date, callback_data=cb.new(id=date, action='date')))
            orders_date_ikm.add(*buttons)
            if MainPage.entries < len(dates):
                orders_date_ikm.add(InlineKeyboardButton(text='↓', callback_data=cb.new(id=0, action='down_page')))
        else:
            for date in dates:
                res_date = str(date)[6:8] + '.' + str(date)[4:6] + '.' + str(date)[2:4]
                buttons.append(InlineKeyboardButton(text=res_date, callback_data=cb.new(id=date, action='date')))
            orders_date_ikm.add(*buttons)
        orders_date_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=-1, action='back')))
        return text, orders_date_ikm

    @staticmethod
    def get_report_for_orders(date: int):
        cb = CallbackData('report_for_orders', 'action')
        report_for_orders_ikm = InlineKeyboardMarkup(row_width=1)
        res_date = str(date)[6:8] + '.' + str(date)[4:6] + '.' + str(date)[2:4]
        text = f'Отчёт по заказам за {res_date}\n'
        text += '--------------------------------------------------\n'
        orders = db.get_orders_by_date(date=date)
        total_sum = 0
        for order in orders:
            text += f'№{order[0]} Пользователем: {order[1]} Сумма: {order[5]}₸\n'
            total_sum += order[5]
        text += '--------------------------------------------------\n'
        text += f'Всего заказов: {len(orders)}\n'
        text += f'Общая сумма всех заказов: {total_sum}₸\n'
        report_for_orders_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(action='back')))
        return text, report_for_orders_ikm

    @staticmethod
    def change_page(state: str):
        if state == 'up_page':
            MainPage.entries -= 10
        if state == 'down_page':
            MainPage.entries += 10

    @staticmethod
    def get_document(doc_id: int, doc_type_id: int) -> tuple:
        cb = CallbackData('document', 'id', 'action')
        document_type_ikm = InlineKeyboardMarkup(row_width=1)
        text = ''
        if doc_type_id == '5':
            order = db.get_data(table='orders', where=1, operand1='id', operand2=doc_id)[0]
            order_items = db.get_data(table='order_items', where=1, operand1='order_id', operand2=doc_id)
            res_date = str(order[2])[6:8] + '.' + str(order[2])[4:6] + '.' + str(order[2])[2:4] + ' ' + str(order[2])[8:10] + ':' + str(order[2])[10:12]
            i, total_cost = 1, 0
            is_paid, is_delivered = ['Не оплачен', 'Оплачен'][order[3]], ['Не доставлен', 'Доставлен'][order[4]]
            text += f'Заказ под номером: {order[0]}' + '\n'
            text += f'Дата: {res_date}' + '\n'
            text += f'Заказан пользователем: {order[1]}' + '\n'
            text += f'Статус оплаты: {is_paid}' + '\n'
            text += f'Статус доставки: {is_delivered}' + '\n'
            for entry in order_items:
                name, cost = db.get_data(get_name_product=1, field1='name', field2='cost', operand1=entry[3])[0]
                text += f'<b>{i}.</b> <b>Название</b> {name}; <b>Кол.</b> {entry[4]}; <b>Сумма</b> {cost * entry[4]}₸.' + '\n'
                total_cost += cost * entry[4]
                i += 1
            text += f'<b>Сумма заказа:</b> {total_cost}₸'
        else:
            # doc_type_id = db.get_doc_type_id(doc_id=doc_id)
            document = db.get_data(table='documents', where=1, operand1='id', operand2=doc_id)[0]
            res_date = str(document[4])[6:8] + '.' + str(document[4])[4:6] + '.' + str(document[4])[2:4] + ' ' + str(document[4])[8:10] + ':' + str(document[4])[10:12]
            if doc_type_id == '1':
                product_name = db.get_data(get_name_product=1, field1='name', operand1=document[2])[0][0]
                text = f'Приходная накладная: №{document[7]}' + '\n'
                text += f'Дата: {res_date}' + '\n'
                text += f'Выполненно: {document[1]}' + '\n'
                text += f'Продукт: {product_name}' + '\n'
                text += f'Добавлено количества: {document[5]}' + '\n'
                text += f'По цене: {document[6]}₸' + '\n'
            elif doc_type_id == '2':
                product_name = db.get_data(get_name_product=1, field1='name', operand1=document[2])[0][0]
                text = f'Расходная накладная: №{document[7]}' + '\n'
                text += f'Дата: {res_date}' + '\n'
                text += f'Выполненно: {document[1]}' + '\n'
                text += f'Продукт: {product_name}' + '\n'
                text += f'Количество списанного: {document[5]}' + '\n'
                text += f'По цене: {document[6]}₸' + '\n'
            elif doc_type_id == '3':
                text = f'Пополнение баланса пользователя: №{document[7]}' + '\n'
                text += f'Дата отправки запроса на пополнение баланса: {res_date}' + '\n'
                text += f'Выполненно: {document[1]}' + '\n'
                text += f'Пользователю: {document[2]}' + '\n'
                text += f'Начислено: {document[6]}₸' + '\n'
            elif doc_type_id == '4':
                text = f'Запрос на пополнение баланса пользователя: №{document[7]}' + '\n'
                text += f'Дата отправки запроса: {res_date}' + '\n'
                text += f'Пользователю: {document[2]}' + '\n'
                user = db.get_data(table='users', where=1, operand1='id', operand2=document[2])[0]
                link = f"https://t.me/{user[5]}"
                text += f'Ссылка на пользователя: {link}'
                document_type_ikm.add(InlineKeyboardButton(text='Выполнить', callback_data=cb.new(id=document[2], action='add_balance')))
        document_type_ikm.add(InlineKeyboardButton(text='Назад', callback_data=cb.new(id=doc_type_id, action='back')))
        return text, document_type_ikm
