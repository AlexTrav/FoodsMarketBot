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
        await callback.message.delete()
        await UserStatesGroup.product.set()
        text, keyboard, photo = Keyboards.get_product(product_id=callback_data['id'], user_id=callback.from_user.id)
        await callback.message.answer_photo(photo=photo,
                                            caption=text,
                                            reply_markup=keyboard)
    await callback.answer()


@dp.callback_query_handler(CallbackData('product', 'id', 'action').filter(), state=[UserStatesGroup.product, UserStatesGroup.adding_to_basket])
async def add_product_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.products.set()
        await callback.message.delete()
        async with state.proxy() as data:
            await callback.message.answer(text='Выберите продукт:',
                                          reply_markup=Keyboards.get_products(subcategory_id=data['product_subcatalog']))
        await callback.answer()
    else:
        await UserStatesGroup.adding_to_basket.set()
        answer, is_delete = db.working_with_basket(state=callback_data['action'], user_id=callback.from_user.id, product_id=callback_data['id'])
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
async def place_an_order_callback_query(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm())
    else:
        if callback_data['action'] == 'edit_basket':
            UserStatesGroup.edit_basket.set()
            # await callback.message.edit_text(text='Редактирование корзины',
            #                                  reply_markup=Keyboards.get_edit_basket(callback_data['orders_entries']))
            await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(product_catalog_callback_query)
    dispatcher.register_callback_query_handler(product_subcatalog_callback_query)
    dispatcher.register_callback_query_handler(products_callback_query)
    dispatcher.register_callback_query_handler(product_callback_query)
    dispatcher.register_callback_query_handler(add_product_callback_query)
    dispatcher.register_callback_query_handler(get_user_basket_callback_query)
    dispatcher.register_callback_query_handler(place_an_order_callback_query)
