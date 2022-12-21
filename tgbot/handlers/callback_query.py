from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMedia
from aiogram.utils.callback_data import CallbackData

from tgbot.loader import dp

from tgbot.classes.states import UserStatesGroup
from tgbot.classes.keyboards import Keyboards

from tgbot.db.database import db


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
                                         reply_markup=Keyboards.get_start_ikm())
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
        await callback.message.edit_text(text='Выберите продукт:',
                                         reply_markup=Keyboards.get_products(subcategory_id=callback_data['id']))
    await callback.answer()


@dp.callback_query_handler(CallbackData('products', 'id', 'action').filter(), state=UserStatesGroup.products)
async def product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.product_subcatalog.set()
        async with state.proxy() as data:
            await callback.message.edit_text(text='Выберите подкатегорию продуктов:',
                                             reply_markup=Keyboards.get_product_subcatalog(category_id=data['product_catalog']))
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


@dp.callback_query_handler(CallbackData('product', 'id', 'action').filter(), state=[UserStatesGroup.product, UserStatesGroup.adding_to_basket])
async def add_product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        if data['edit_basket'] == -2:
            answer, is_delete = db.working_with_basket(state=callback_data['action'], user_id=callback.from_user.id,
                                                       product_id=callback_data['id'])
            if callback_data['action'] == 'add_basket_count' or callback_data['action'] == 'dec_basket_count' and is_delete:
                text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id, back_id=-2)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            await callback.answer(text=answer)
            if callback_data['action'] == 'back':
                await callback.message.delete()
                await UserStatesGroup.edit_basket.set()
                text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
                await callback.message.answer(text=text,
                                              reply_markup=keyboard)
                await callback.answer()
        elif callback_data['action'] == 'back':
            await callback.message.delete()
            if callback_data['id'] == '-1':
                await UserStatesGroup.products.set()
                await callback.message.answer(text='Выберите продукт:',
                                              reply_markup=Keyboards.get_products(subcategory_id=data['product_subcatalog']))
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
                text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id)
                await callback.message.edit_media(InputMedia(media=photo, caption=text), reply_markup=keyboard)
            await callback.answer(text=answer)


@dp.callback_query_handler(text='my_basket',  state='*')
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
                                         reply_markup=Keyboards.get_start_ikm())
    else:
        if callback_data['action'] == 'place_an_order':
            pass
            # if db.get_data(table='basket', where=1, operand1='user_id', operand2=callback.from_user.id):
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
            text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id, states_previous=prev_state)
            await callback.message.answer_photo(photo=photo,
                                                caption=text,
                                                reply_markup=keyboard)
        elif callback_data['action'] == 'dec':
            answer, is_delete = db.working_with_basket(state='dec_basket_count', user_id=callback.from_user.id, product_id=callback_data['id'])
            text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
            await callback.answer(text=answer)
        elif callback_data['action'] == 'inc':
            answer, is_delete = db.working_with_basket(state='inc_basket_count', user_id=callback.from_user.id, product_id=callback_data['id'])
            text, keyboard = Keyboards.get_edit_basket(user_id=callback.from_user.id)
            await callback.message.edit_text(text=text,
                                             reply_markup=keyboard)
            await callback.answer(text=answer)
        elif callback_data['action'] == '':
            await callback.answer(text='Количетсво товара:')

    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(product_catalog_callback_query)
    dispatcher.register_callback_query_handler(product_subcatalog_callback_query)
    dispatcher.register_callback_query_handler(products_callback_query)
    dispatcher.register_callback_query_handler(product_callback_query)
    dispatcher.register_callback_query_handler(add_product_callback_query)
    dispatcher.register_callback_query_handler(get_user_basket_callback_query)
    dispatcher.register_callback_query_handler(place_an_order_callback_query)
    dispatcher.register_callback_query_handler(edit_basket_callback_query)
