from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMedia
from aiogram.utils.callback_data import CallbackData

from tgbot.loader import dp

from tgbot.classes.states import UserStatesGroup, CourierStatesGroup, OperatorStatesGroup, AdminStatesGroup
from tgbot.classes.keyboards import Keyboards

from tgbot.db.database import db

from tgbot.variables.config import MainPage, Products


@dp.callback_query_handler(text='exit', state='*')
async def exit_callback_query(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    db.exit_role(user_id=callback.from_user.id)
    await callback.answer('Вы успешно вышли!')
    await callback.message.delete()


#######################################################################USER#########################################################################################

@dp.callback_query_handler(CallbackData('del_message', 'action').filter(), state='*')
async def my_balance_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.my_profile.set()
        text, keyboard = Keyboards.get_profile(callback.from_user.id)
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
    else:
        await callback.answer('Сообщение удалено')
        await callback.message.delete()
    await callback.answer()


@dp.callback_query_handler(text='product_catalog', state='*')
async def product_catalog_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.product_catalog.set()
    await callback.message.edit_text(text='Выберите категорию продуктов:',
                                     reply_markup=Keyboards.get_product_catalog())
    await callback.answer()


@dp.callback_query_handler(CallbackData('categories', 'id', 'action').filter(), state=UserStatesGroup.product_catalog)
async def product_subcatalog_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm(callback.from_user.id))
    else:
        await UserStatesGroup.product_subcatalog.set()
        async with state.proxy() as data:
            data['product_catalog'] = callback_data['id']
        await callback.message.edit_text(text='Выберите подкатегорию продуктов:',
                                         reply_markup=Keyboards.get_product_subcatalog(category_id=callback_data['id']))
    await callback.answer()


@dp.callback_query_handler(CallbackData('subcategories', 'id', 'action').filter(), state=UserStatesGroup.product_subcatalog)
async def products_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.product_catalog.set()
        await callback.message.edit_text(text='Выберите категорию продуктов:',
                                         reply_markup=Keyboards.get_product_catalog())
    else:
        async with state.proxy() as data:
            data['product_subcatalog'] = callback_data['id']
        await UserStatesGroup.products.set()
        MainPage.entries = 10
        Products.sorting = ''
        await callback.message.edit_text(text='Выберите продукт:',
                                         reply_markup=Keyboards.get_products(subcategory_id=callback_data['id']))
    await callback.answer()


@dp.callback_query_handler(CallbackData('products', 'id', 'action').filter(), state=UserStatesGroup.products)
async def product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.product_subcatalog.set()
        async with state.proxy() as data:
            await callback.message.edit_text(text='Выберите подкатегорию продуктов:',
                                             reply_markup=Keyboards.get_product_subcatalog(
                                                 category_id=data['product_catalog']))
    else:
        if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
            Keyboards.change_page(callback_data['action'])
            await UserStatesGroup.products.set()
            await callback.message.edit_text(text='Выберите продукт:',
                                             reply_markup=Keyboards.get_products(subcategory_id=callback_data['id']))
        elif callback_data['action'] == 'sorting':
            text, keyboard = Keyboards.get_sorting_form(callback_data['id'])
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
        else:
            async with state.proxy() as data:
                data['edit_basket'] = ''
            await callback.message.delete()
            await UserStatesGroup.product.set()
            text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id)
            await callback.message.answer_photo(photo=photo,
                                                caption=text,
                                                reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('sorting', 'id', 'action').filter(), state=UserStatesGroup.products)
async def sorting_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await callback.message.edit_text(text='Выберите продукт:',
                                         reply_markup=Keyboards.get_products(subcategory_id=callback_data['id']))
    else:
        answer = Keyboards.get_sorting(state=callback_data['action'])
        await callback.message.edit_text(text='Выберите продукт:',
                                         reply_markup=Keyboards.get_products(subcategory_id=callback_data['id']))
        await callback.answer(answer)
    await callback.answer()


@dp.callback_query_handler(CallbackData('product', 'id', 'action').filter(), state=[UserStatesGroup.product, UserStatesGroup.adding_to_basket])
async def add_product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        if data['edit_basket'] == -3:
            if callback_data['id'] == '-1':
                await callback.message.delete()
                text, keyboard = Keyboards.get_search_products(search_query=data['search_query'])
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
                await UserStatesGroup.search.set()
            else:
                answer, is_delete = db.working_with_basket(state=callback_data['action'], user_id=callback.from_user.id,
                                                           product_id=callback_data['id'])
                await UserStatesGroup.adding_to_basket.set()
                if callback_data['action'] == 'add_basket_count' or callback_data['action'] == 'dec_basket_count' and is_delete:
                    text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'],
                                                                  user_id=callback.from_user.id)
                    await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
                await callback.answer(text=answer)
        elif data['edit_basket'] == -2:
            answer, is_delete = db.working_with_basket(state=callback_data['action'], user_id=callback.from_user.id,
                                                       product_id=callback_data['id'])
            if callback_data['action'] == 'add_basket_count' or callback_data['action'] == 'dec_basket_count' and is_delete:
                text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'],
                                                              user_id=callback.from_user.id, back_id=-2)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
                await callback.answer(text=answer)
            elif callback_data['action'] == 'back':
                await callback.message.delete()
                await UserStatesGroup.edit_basket.set()
                text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
                await callback.answer()
            # await callback.message.delete()
            elif callback_data['id'] == '-1':
                await UserStatesGroup.products.set()
                await callback.message.answer(text='Выберите продукт:',
                                              reply_markup=Keyboards.get_products(
                                                  subcategory_id=data['product_subcatalog']))
            else:
                await UserStatesGroup.edit_basket.set()
                text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
            await callback.answer()
        else:
            answer, is_delete = db.working_with_basket(state=callback_data['action'], user_id=callback.from_user.id,
                                                       product_id=callback_data['id'])
            await UserStatesGroup.adding_to_basket.set()
            if callback_data['action'] == 'add_basket_count' or callback_data['action'] == 'dec_basket_count' and is_delete:
                text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'],
                                                              user_id=callback.from_user.id)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            if callback_data['id'] == '-1':
                await callback.message.delete()
                await UserStatesGroup.products.set()
                await callback.message.answer(text='Выберите продукт:',
                                              reply_markup=Keyboards.get_products(
                                                  subcategory_id=data['product_subcatalog']))
            await callback.answer(text=answer)
    await callback.answer()


@dp.callback_query_handler(text='my_basket', state='*')
async def get_user_basket_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.my_basket.set()
    text, keyboard = Keyboards.get_basket(callback.from_user.id)
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard,
                                     parse_mode='HTML')
    await callback.answer()


@dp.callback_query_handler(CallbackData('basket', 'action').filter(), state=UserStatesGroup.my_basket)
async def place_an_order_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm(callback.from_user.id))
    else:
        if callback_data['action'] == 'place_an_order':
            answer = Keyboards.place_an_order(user_id=callback.from_user.id)
            if answer != 'Корзина пуста! Сначало добавьте товар!':
                text, keyboard = Keyboards.get_basket(callback.from_user.id)
                await callback.message.edit_text(text=text,
                                                 reply_markup=keyboard,
                                                 parse_mode='HTML')
            await callback.answer(answer)
        else:
            await UserStatesGroup.edit_basket.set()
            text, keyboard = Keyboards.get_edit_basket(callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
            await callback.answer()


@dp.callback_query_handler(CallbackData('edit_basket', 'id', 'action').filter(), state=UserStatesGroup.edit_basket)
async def edit_basket_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.my_basket.set()
        text, keyboard = Keyboards.get_basket(callback.from_user.id)
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
    else:
        if callback_data['action'] == 'open_product':
            async with state.proxy() as data:
                data['edit_basket'] = -2
            prev_state = await state.get_state()
            await callback.message.delete()
            await UserStatesGroup.product.set()
            text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id,
                                                          states_previous=prev_state)
            await callback.message.answer_photo(photo=photo,
                                                caption=text,
                                                reply_markup=keyboard)
        elif callback_data['action'] == 'dec':
            answer, is_delete = db.working_with_basket(state='dec_basket_count', user_id=callback.from_user.id,
                                                       product_id=callback_data['id'])
            text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
            await callback.answer(text=answer)
        elif callback_data['action'] == 'inc':
            answer, is_delete = db.working_with_basket(state='inc_basket_count', user_id=callback.from_user.id,
                                                       product_id=callback_data['id'])
            text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
            await callback.answer(text=answer)
        else:
            await callback.answer(text='Количетсво товара:')

    await callback.answer()


@dp.callback_query_handler(text='my_orders', state='*')
async def get_user_orders_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.my_orders.set()
    MainPage.entries = 10
    await callback.message.edit_text(text='Мои заказы:',
                                     reply_markup=Keyboards.get_orders(callback.from_user.id))
    await callback.answer()


@dp.callback_query_handler(CallbackData('orders', 'id', 'action').filter(), state=UserStatesGroup.my_orders)
async def open_order_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm(callback.from_user.id))
    else:
        if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
            Keyboards.change_page(callback_data['action'])
            await UserStatesGroup.my_orders.set()
            await callback.message.edit_text(text='Мои заказы:',
                                             reply_markup=Keyboards.get_orders(callback.from_user.id))
        else:
            if callback_data['action'] == 'order_item':
                await UserStatesGroup.order_item.set()
                text, keyboard = Keyboards.get_order_item(order_id=int(callback_data['id']))
                await callback.message.edit_text(text=text,
                                                 reply_markup=keyboard,
                                                 parse_mode='HTML')
            if callback_data['action'] == 'is_paid':
                await callback.answer('Оплачен ли заказ')
            if callback_data['action'] == 'is_delivered':
                await callback.answer('Доставлен ли заказ')


@dp.callback_query_handler(CallbackData('order_item', 'id', 'action').filter(), state=UserStatesGroup.order_item)
async def order_payment_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.my_orders.set()
        await callback.message.edit_text(text='Мои заказы:',
                                         reply_markup=Keyboards.get_orders(callback.from_user.id))
        await callback.answer()
    else:
        if callback_data['action'] == 'to_pay':
            if db.check_enough_money(user_id=callback.from_user.id,
                                     sum=Keyboards.get_total_cost(order_id=callback_data['id'])):
                if db.check_address(user_id=callback.from_user.id):
                    db.order_payment(user_id=callback.from_user.id, order_id=callback_data['id'],
                                     sum=Keyboards.get_total_cost(order_id=callback_data['id']))
                    db.working_with_place_an_order(insert_in_delivery=1, order_id=callback_data['id'])
                    text, keyboard = Keyboards.get_order_item(order_id=callback_data['id'])
                    await callback.message.edit_text(text=text,
                                                     reply_markup=keyboard,
                                                     parse_mode='HTML')
                    await callback.answer('Заказ успешно оплачен и отправлен на доставку! Ожидайте звонка курьера!')
                else:
                    await callback.answer('Адрес доставки не указан, укажите его в профиле!')
            else:
                await callback.answer('У вас не достаточно средств!')
        if callback_data['action'] == 'paid_for':
            await callback.answer('Заказ уже оплачен')
        if callback_data['action'] == 'not_delivered':
            await callback.answer('Заказ ещё не доставлен')
        if callback_data['action'] == 'delivered':
            await callback.answer('Заказ уже доставлен')


@dp.callback_query_handler(text='profile', state='*')
async def get_user_profile_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.my_profile.set()
    text, keyboard = Keyboards.get_profile(callback.from_user.id)
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard,
                                     parse_mode='HTML')
    await callback.answer()


@dp.callback_query_handler(CallbackData('user_profile', 'action').filter(), state=UserStatesGroup.my_profile)
async def user_profile_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm(callback.from_user.id))
    else:
        if callback_data['action'] == 'add_balance':
            answer = Keyboards.add_balance_user(user_id=callback.from_user.id)
            await callback.answer(answer)
        if callback_data['action'] == 'set_location' or callback_data['action'] == 'update_location':
            await callback.message.delete()
            await UserStatesGroup.add_address.set()
            text, keyboard = Keyboards.get_location_user_form()
            await callback.message.answer(text=text,
                                          reply_markup=keyboard)
        if callback_data['action'] == 'set_phone':
            await callback.message.delete()
            await UserStatesGroup.add_phone.set()
            text, keyboard = Keyboards.get_phone_user_form()
            await callback.message.answer(text=text,
                                          reply_markup=keyboard)
        if callback_data['action'] == 'list_admins':
            await UserStatesGroup.list_admins.set()
            MainPage.entries = 10
            text, keyboard = Keyboards.get_list_admins(callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('list_admins', 'id', 'action').filter(), state=UserStatesGroup.list_admins)
async def list_admins_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.my_profile.set()
        text, keyboard = Keyboards.get_profile(callback.from_user.id)
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
    else:
        if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
            Keyboards.change_page(callback_data['action'])
            text, keyboard = Keyboards.get_list_admins(callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)


@dp.callback_query_handler(text='work', state='*')
async def get_work_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.work.set()
    text, keyboard = Keyboards.get_work()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('work', 'action').filter(), state=UserStatesGroup.work)
async def working_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm(callback.from_user.id))
    else:
        if callback_data['action'] == 'admin':
            answer = db.check_role(user_id=callback.from_user.id, role_id=4)
            await callback.answer(answer)
            if answer != 'Вас нету в списке работников!':
                await callback.message.delete()
        if callback_data['action'] == 'operator':
            answer = db.check_role(user_id=callback.from_user.id, role_id=2)
            await callback.answer(answer)
            if answer != 'Вас нету в списке работников!':
                await callback.message.delete()
        if callback_data['action'] == 'courier':
            answer = db.check_role(user_id=callback.from_user.id, role_id=3)
            await callback.answer(answer)
            if answer != 'Вас нету в списке работников!':
                await callback.message.delete()
    await callback.answer()


@dp.callback_query_handler(text='search', state='*')
async def get_search_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.search.set()
    text, keyboard = Keyboards.get_search()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('back', 'action').filter(), state=UserStatesGroup.search)
async def back_search_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'delete':
        await callback.message.delete()
    else:
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm(callback.from_user.id))
        await callback.answer()


@dp.callback_query_handler(CallbackData('search_answer', 'id', 'action').filter(), state=UserStatesGroup.search)
async def search_answer_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        text, keyboard = Keyboards.get_search()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
            Keyboards.change_page(callback_data['action'])
            text, keyboard = Keyboards.get_search_products(search_query=callback_data['id'])
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
        if callback_data['action'] == 'search_product':
            async with state.proxy() as data:
                data['edit_basket'] = -3
            await callback.message.delete()
            await UserStatesGroup.product.set()

            text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id)
            await callback.message.answer_photo(photo=photo,
                                                caption=text,
                                                reply_markup=keyboard)
    await callback.answer()


#######################################################################OPERATOR####################################################################################

@dp.callback_query_handler(text='products', state=OperatorStatesGroup.start)
async def working_warehouse_callback_query(callback: types.CallbackQuery):
    await OperatorStatesGroup.working_warehouse.set()
    text, keyboard = Keyboards.get_working_warehouse()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('working_warehouse', 'action').filter(), state=OperatorStatesGroup.working_warehouse)
async def operator_functions_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        role_id = db.get_role_id(user_id=callback.from_user.id)
        if role_id == 4:
            await AdminStatesGroup.start.set()
            await callback.message.edit_text(text='Админ! Добро пожаловать в FoodsMarket!',
                                             reply_markup=Keyboards.get_start_admin())
        else:
            await OperatorStatesGroup.start.set()
            await callback.message.edit_text(text='Оператор! Добро пожаловать в FoodsMarket!',
                                             reply_markup=Keyboards.get_start_operator())
    else:
        if callback_data['action'] == 'add_product':
            await OperatorStatesGroup.add_product.set()
            text, keyboard = Keyboards.get_add_product()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard,
                                             parse_mode='HTML')
        if callback_data['action'] == 'arrival_product' or callback_data['action'] == 'write_off_product':
            OperatorStatesGroup.state = callback_data['action']
            text, keyboard = Keyboards.get_search_working_warehouse()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('search_working_warehouse', 'action').filter(), state='*')
async def search_working_warehouse_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        OperatorStatesGroup.state = ''
        await OperatorStatesGroup.working_warehouse.set()
        text, keyboard = Keyboards.get_working_warehouse()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        if callback_data['action'] == 'search_id':
            await OperatorStatesGroup.search_id.set()
            text, keyboard = Keyboards.get_search_id()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
            await callback.answer()
        if callback_data['action'] == 'search':
            await OperatorStatesGroup.search.set()
            text, keyboard = Keyboards.get_search()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('back', 'action').filter(), state=OperatorStatesGroup.search)
async def operator_back_search_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'delete':
        await callback.message.delete()
    else:
        text, keyboard = Keyboards.get_search_working_warehouse()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
        await callback.answer()


@dp.callback_query_handler(CallbackData('back', 'action').filter(), state=OperatorStatesGroup.search_id)
async def operator_back_search_id_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'delete':
        await callback.message.delete()
    else:
        text, keyboard = Keyboards.get_search_working_warehouse()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
        await callback.answer()


@dp.callback_query_handler(CallbackData('search_answer', 'id', 'action').filter(), state=OperatorStatesGroup.search)
async def operator_search_answer_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        text, keyboard = Keyboards.get_search()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
            Keyboards.change_page(callback_data['action'])
            text, keyboard = Keyboards.get_search_products(search_query=callback_data['id'])
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
        if callback_data['action'] == 'search_product':
            await callback.message.delete()
            await OperatorStatesGroup.product.set()
            text, keyboard, photo = Keyboards.get_product_operator(product_id=callback_data['id'], state=OperatorStatesGroup.state)
            await callback.message.answer_photo(photo=photo,
                                                caption=text,
                                                reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('search_answer', 'id', 'action').filter(), state=OperatorStatesGroup.search_id)
async def operator_search_id_answer_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        text, keyboard = Keyboards.get_search_id()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        if callback_data['action'] == 'search_product':
            await callback.message.delete()
            await OperatorStatesGroup.product.set()
            text, keyboard, photo = Keyboards.get_product_operator(product_id=callback_data['id'], state=OperatorStatesGroup.state)
            await callback.message.answer_photo(photo=photo,
                                                caption=text,
                                                reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('arrival_product', 'id', 'action').filter(), state=OperatorStatesGroup.product)
async def arrival_product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await OperatorStatesGroup.search.set()
        await callback.message.delete()
        async with state.proxy() as data:
            if data['back_id'] == 1:
                text, keyboard = Keyboards.get_search_products(search_query=data['search_query'])
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
            else:
                text, keyboard = Keyboards.get_search_id_product(search_id=data['search_id'])
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
    else:
        if callback_data['action'] == 'dec_count_product' or callback_data['action'] == 'inc_count_product':
            answer = Keyboards.get_answer_operator_arrival_product(callback_data['action'])
            if answer != 'Добавленное количество не может быть меньше 0':
                text, keyboard, photo = Keyboards.get_product_operator(product_id=callback_data['id'], state=OperatorStatesGroup.state)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            await callback.answer(answer)
        if callback_data['action'] == 'count_product':
            await callback.answer('Количество добавленного товара:')
        if callback_data['action'] == 'change_price':
            await callback.message.delete()
            await OperatorStatesGroup.change_price.set()
            async with state.proxy() as data:
                data['product_id'] = callback_data['id']
            text, keyboard = Keyboards.get_change_price_product()
            await callback.message.answer(text=text,
                                          reply_markup=keyboard)
        if callback_data['action'] == 'save':
            answer = Keyboards.saving_the_operator_work(callback_data['id'], callback.from_user.id)
            if answer != 'Чтобы сохранить, измените что нибудь!':
                text, keyboard, photo = Keyboards.get_product_operator(product_id=callback_data['id'], state=OperatorStatesGroup.state)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            await callback.answer(answer)


@dp.callback_query_handler(CallbackData('write_off_product', 'id', 'action').filter(), state=OperatorStatesGroup.product)
async def write_off_product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await OperatorStatesGroup.search.set()
        await callback.message.delete()
        async with state.proxy() as data:
            if data['back_id'] == 1:
                text, keyboard = Keyboards.get_search_products(search_query=data['search_query'])
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
            else:
                text, keyboard = Keyboards.get_search_id_product(search_id=data['search_id'])
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
    else:
        if callback_data['action'] == 'dec_count_product' or callback_data['action'] == 'inc_count_product':
            answer = Keyboards.get_answer_operator_write_off_product(callback_data['action'])
            if answer != 'Количество списанного не может быть меньше 0':
                text, keyboard, photo = Keyboards.get_product_operator(product_id=callback_data['id'], state=OperatorStatesGroup.state)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            await callback.answer(answer)
        if callback_data['action'] == 'count_product':
            await callback.answer('Количество добавленного товара:')
        if callback_data['action'] == 'write_off':
            answer = Keyboards.write_off_product_work(callback_data['id'], callback.from_user.id)
            if answer != 'Чтобы списать, измените что нибудь!' and answer != 'Нельзя списать, больше чем есть на складе!':
                text, keyboard, photo = Keyboards.get_product_operator(product_id=callback_data['id'], state=OperatorStatesGroup.state)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            await callback.answer(answer)


@dp.callback_query_handler(CallbackData('change_price', 'action').filter(), state=OperatorStatesGroup.change_price)
async def operator_back_product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'delete':
        await callback.answer('Сообщение удалено')
        await callback.message.delete()
    else:
        await callback.message.delete()
        await OperatorStatesGroup.product.set()
        async with state.proxy() as data:
            text, keyboard, photo = Keyboards.get_product_operator(product_id=data['product_id'], state=OperatorStatesGroup.state)
        await callback.message.answer_photo(photo=photo,
                                            caption=text,
                                            reply_markup=keyboard)


@dp.callback_query_handler(CallbackData('add_product_msg', 'action').filter(), state=OperatorStatesGroup.add_product)
async def add_product_msg_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'delete':
        await callback.answer('Сообщение удалено')
        await callback.message.delete()
    else:
        if callback_data['action'] == 'select_subcategory':
            await OperatorStatesGroup.select_subcategory.set()
            keyboard = Keyboards.get_product_catalog()
            await callback.message.edit_text(text='Выберите категорию продуктов:',
                                             reply_markup=keyboard)
        else:
            await OperatorStatesGroup.working_warehouse.set()
            text, keyboard = Keyboards.get_working_warehouse()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('categories', 'id', 'action').filter(), state=OperatorStatesGroup.select_subcategory)
async def select_category_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await OperatorStatesGroup.add_product.set()
        text, keyboard = Keyboards.get_add_product()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
    else:
        async with state.proxy() as data:
            data['product_catalog'] = callback_data['id']
        await callback.message.edit_text(text='Выберите подкатегорию продуктов:',
                                         reply_markup=Keyboards.get_product_subcatalog(category_id=callback_data['id']))
    await callback.answer()


@dp.callback_query_handler(CallbackData('subcategories', 'id', 'action').filter(), state=OperatorStatesGroup.select_subcategory)
async def select_subcategory_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await callback.message.edit_text(text='Выберите категорию продуктов:',
                                         reply_markup=Keyboards.get_product_catalog())
    else:
        answer = Keyboards.get_answer_subcategory(callback_data['id'])
        await OperatorStatesGroup.add_product.set()
        text, keyboard = Keyboards.get_add_product()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
        await callback.answer(answer)
    await callback.answer()


#######################################################################COURIER#####################################################################################

@dp.callback_query_handler(text='orders', state=CourierStatesGroup.start)
async def undelivered_orders_callback_query(callback: types.CallbackQuery):
    await CourierStatesGroup.orders.set()
    text, keyboard = Keyboards.get_undelivered_orders()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('delivery', 'id', 'action').filter(), state=CourierStatesGroup.orders)
async def delivery_orders_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await CourierStatesGroup.start.set()
        await callback.message.edit_text(text='Курьер! Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_courier())
    else:
        await CourierStatesGroup.order_item.set()
        text, keyboard = Keyboards.get_order_item_courier(order_id=callback_data['id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
        await callback.answer()


@dp.callback_query_handler(CallbackData('order_item', 'id', 'action').filter(), state=CourierStatesGroup.order_item)
async def delivered_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await CourierStatesGroup.orders.set()
        text, keyboard = Keyboards.get_undelivered_orders()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
        await callback.answer()
    else:
        client_id = db.delivered_order(user_id=callback.from_user.id, order_id=callback_data['id'])[0]
        text = f'Заказ под номером: {callback_data["id"]} - доставлен!'
        await dp.bot.send_message(client_id, text=text)
        await CourierStatesGroup.orders.set()
        text, keyboard = Keyboards.get_undelivered_orders()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
        await callback.answer('Заказ успешно выполнен!')


#######################################################################ADMIN##########################################################################################

@dp.callback_query_handler(text='products', state=AdminStatesGroup.start)
async def working_warehouse_callback_query_admin(callback: types.CallbackQuery):
    await OperatorStatesGroup.working_warehouse.set()
    text, keyboard = Keyboards.get_working_warehouse()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(text='users', state=AdminStatesGroup.start)
async def users_callback_query_admin(callback: types.CallbackQuery):
    await AdminStatesGroup.users.set()
    text, keyboard = Keyboards.get_users()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(text='documents', state=AdminStatesGroup.start)
async def document_types_callback_query_admin(callback: types.CallbackQuery):
    await AdminStatesGroup.documents.set()
    text, keyboard = Keyboards.get_document_types()
    await callback.message.edit_text(text=text,
                                     reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('users', 'action').filter(), state=AdminStatesGroup.users)
async def working_with_users_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await AdminStatesGroup.start.set()
        await callback.message.edit_text(text='Админ! Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_admin())
    else:
        if callback_data['action'] == 'give_role':
            await AdminStatesGroup.give_role_user.set()
            text, keyboard = Keyboards.get_users_()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
        if callback_data['action'] == 'add_balance':
            await AdminStatesGroup.add_balance.set()
            text, keyboard = Keyboards.get_users_()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)


@dp.callback_query_handler(CallbackData('users_', 'id', 'action').filter(), state='*')
async def set_user_or_search_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await AdminStatesGroup.users.set()
        text, keyboard = Keyboards.get_users()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
            Keyboards.change_page(callback_data['action'])
            text, keyboard = Keyboards.get_users_()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
        if callback_data['action'] == 'user':
            current_state = await state.get_state()
            if current_state == 'AdminStatesGroup:give_role_user':
                text, keyboard = Keyboards.get_user_roles(user_id=callback_data['id'])
                await callback.message.edit_text(text=text,
                                                 reply_markup=keyboard)
            if current_state == 'AdminStatesGroup:add_balance':
                text, keyboard = Keyboards.get_user_inf(user_id=callback_data['id'])
                await callback.message.edit_text(text=text,
                                                 reply_markup=keyboard,
                                                 parse_mode='HTML')
        if callback_data['action'] == 'search':
            text, keyboard = Keyboards.set_username()
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('set_username', 'action').filter(), state='*')
async def set_username_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'delete':
        await callback.message.delete()
    else:
        await AdminStatesGroup.users.set()
        text, keyboard = Keyboards.get_users()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
        await callback.answer()


@dp.callback_query_handler(CallbackData('roles_info', 'id', 'action').filter(), state=AdminStatesGroup.give_role_user)
async def working_roles_user_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await AdminStatesGroup.users.set()
        text, keyboard = Keyboards.get_users()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        db.working_with_roles(action=callback_data['action'], user_id=callback_data['id'])
        text, keyboard = Keyboards.get_user_roles(user_id=callback_data['id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)


@dp.callback_query_handler(CallbackData('user_info', 'id', 'action').filter(), state=AdminStatesGroup.add_balance)
async def user_info_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await AdminStatesGroup.users.set()
        text, keyboard = Keyboards.get_users()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        async with state.proxy() as data:
            data['back_id'] = 1
        await AdminStatesGroup.add_balance_user.set()
        text, keyboard = Keyboards.get_add_balance_form(callback_data['id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('back', 'id', 'action').filter(), state=AdminStatesGroup.add_balance_user)
async def add_balance_user_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'delete':
        await callback.message.delete()
    else:
        async with state.proxy() as data:
            if data['back_id'] == 2:
                text, keyboard = Keyboards.get_document(data['document_id'], data['doc_type_id'])
                await callback.message.edit_text(text=text,
                                                 reply_markup=keyboard)
            else:
                text, keyboard = Keyboards.get_user_inf(callback_data['id'])
                await callback.message.edit_text(text=text,
                                                 reply_markup=keyboard,
                                                 parse_mode='HTML')


@dp.callback_query_handler(CallbackData('document_types', 'id', 'action').filter(), state=AdminStatesGroup.documents)
async def get_documents_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await AdminStatesGroup.start.set()
        await callback.message.edit_text(text='Админ! Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_admin())
    else:
        MainPage.entries = 10
        text, keyboard = Keyboards.get_documents(callback_data['id'])
        async with state.proxy() as data:
            data['doc_type_id'] = callback_data['id']
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('document', 'id', 'action').filter(), state=AdminStatesGroup.documents)
async def get_document_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        text, keyboard = Keyboards.get_document_types()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    if callback_data['action'] == 'generate_report':
        text, keyboard = Keyboards.get_orders_date()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
        Keyboards.change_page(callback_data['action'])
        text, keyboard = Keyboards.get_documents(callback_data['id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    if callback_data['action'] == 'document':
        await AdminStatesGroup.document.set()
        async with state.proxy() as data:
            text, keyboard = Keyboards.get_document(callback_data['id'], data['doc_type_id'])
            data['document_id'] = callback_data['id']
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
    await callback.answer()


@dp.callback_query_handler(CallbackData('date', 'id', 'action').filter(), state=AdminStatesGroup.documents)
async def generate_report(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        async with state.proxy() as data:
            text, keyboard = Keyboards.get_documents(data['doc_type_id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    if callback_data['action'] == 'up_page' or callback_data['action'] == 'down_page':
        Keyboards.change_page(callback_data['action'])
        text, keyboard = Keyboards.get_orders_date()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    if callback_data['action'] == 'date':
        text, keyboard = Keyboards.get_report_for_orders(callback_data['id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('report_for_orders', 'action').filter(), state=AdminStatesGroup.documents)
async def back_report(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        text, keyboard = Keyboards.get_orders_date()
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)


@dp.callback_query_handler(CallbackData('document', 'id', 'action').filter(), state=AdminStatesGroup.document)
async def get_back_document_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await AdminStatesGroup.documents.set()
        text, keyboard = Keyboards.get_documents(callback_data['id'])
        await callback.message.edit_text(text=text,
                                         reply_markup=keyboard)
    else:
        if callback_data['action'] == 'add_balance':
            await AdminStatesGroup.add_balance_user.set()
            async with state.proxy() as data:
                data['back_id'] = 2
            text, keyboard = Keyboards.get_add_balance_form(callback_data['id'])
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)

###################################################################REGISTER_HANDLERS##################################################################################


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(exit_callback_query)
    ###################################USER###################################
    dispatcher.register_callback_query_handler(product_catalog_callback_query)
    dispatcher.register_callback_query_handler(product_subcatalog_callback_query)
    dispatcher.register_callback_query_handler(products_callback_query)
    dispatcher.register_callback_query_handler(product_callback_query)
    dispatcher.register_callback_query_handler(add_product_callback_query)
    dispatcher.register_callback_query_handler(get_user_basket_callback_query)
    dispatcher.register_callback_query_handler(place_an_order_callback_query)
    dispatcher.register_callback_query_handler(edit_basket_callback_query)
    dispatcher.register_callback_query_handler(open_order_callback_query)
    dispatcher.register_callback_query_handler(get_user_profile_callback_query)
    dispatcher.register_callback_query_handler(user_profile_callback_query)
    dispatcher.register_callback_query_handler(get_work_callback_query)
    dispatcher.register_callback_query_handler(working_callback_query)
    dispatcher.register_callback_query_handler(get_search_callback_query)
    dispatcher.register_callback_query_handler(back_search_callback_query)
    dispatcher.register_callback_query_handler(search_answer_callback_query)
    dispatcher.register_callback_query_handler(sorting_callback_query)
    dispatcher.register_callback_query_handler(list_admins_callback_query)
    ##################################OPERATOR################################
    dispatcher.register_callback_query_handler(working_warehouse_callback_query)
    dispatcher.register_callback_query_handler(operator_functions_callback_query)
    dispatcher.register_callback_query_handler(search_working_warehouse_callback_query)
    dispatcher.register_callback_query_handler(operator_back_search_callback_query)
    dispatcher.register_callback_query_handler(operator_back_search_id_callback_query)
    dispatcher.register_callback_query_handler(operator_search_answer_callback_query)
    dispatcher.register_callback_query_handler(operator_search_id_answer_callback_query)
    dispatcher.register_callback_query_handler(arrival_product_callback_query)
    dispatcher.register_callback_query_handler(write_off_product_callback_query)
    dispatcher.register_callback_query_handler(operator_back_product_callback_query)
    dispatcher.register_callback_query_handler(add_product_msg_callback_query)
    dispatcher.register_callback_query_handler(select_category_callback_query)
    dispatcher.register_callback_query_handler(select_subcategory_callback_query)
    ##################################COURIER#################################
    dispatcher.register_callback_query_handler(undelivered_orders_callback_query)
    dispatcher.register_callback_query_handler(delivery_orders_callback_query)
    dispatcher.register_callback_query_handler(delivered_callback_query)
    ##################################ADMIN###################################
    dispatcher.register_callback_query_handler(working_warehouse_callback_query_admin)
    dispatcher.register_callback_query_handler(users_callback_query_admin)
    dispatcher.register_callback_query_handler(working_with_users_callback_query)
    dispatcher.register_callback_query_handler(set_user_or_search_callback_query)
    dispatcher.register_callback_query_handler(set_username_callback_query)
    dispatcher.register_callback_query_handler(working_roles_user_callback_query)
    dispatcher.register_callback_query_handler(user_info_callback_query)
    dispatcher.register_callback_query_handler(add_balance_user_callback_query)
    dispatcher.register_message_handler(document_types_callback_query_admin)
    dispatcher.register_callback_query_handler(get_documents_callback_query)
    dispatcher.register_callback_query_handler(get_document_callback_query)
    dispatcher.register_callback_query_handler(get_back_document_callback_query)
