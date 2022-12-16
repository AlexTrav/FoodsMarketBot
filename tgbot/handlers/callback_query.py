from aiogram import types, Dispatcher
from aiogram.utils.callback_data import CallbackData

from tgbot.loader import dp

from tgbot.classes.states import UserStatesGroup
from tgbot.classes.keyboards import Keyboards


@dp.callback_query_handler(text='product_catalog', state=UserStatesGroup.start)
async def product_catalog_callback_query(callback: types.CallbackQuery):
    await UserStatesGroup.product_catalog.set()
    await callback.message.edit_text(text='Выберите категорию продуктов:',
                                     reply_markup=Keyboards.get_product_catalog())
    await callback.answer()


@dp.callback_query_handler(CallbackData('categories', 'id', 'action').filter(), state=UserStatesGroup.product_catalog)
async def product_subcatalog_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.start.set()
        await callback.message.edit_text(text='Добро пожаловать в FoodsMarket!',
                                         reply_markup=Keyboards.get_start_ikm())
    else:
        await UserStatesGroup.product_subcatalog.set()
        await callback.message.edit_text(text='Выберите подкатегорию продуктов:',
                                         reply_markup=Keyboards.get_product_subcatalog(category_id=callback_data['id']))
    await callback.answer()


@dp.callback_query_handler(CallbackData('subcategories', 'id', 'action').filter(), state=UserStatesGroup.product_subcatalog)
async def products_callback_query(callback: types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'back':
        await UserStatesGroup.product_catalog.set()
        await callback.message.edit_text(text='Выберите категорию продуктов:',
                                         reply_markup=Keyboards.get_product_catalog())
    else:
        await UserStatesGroup.products.set()
        await callback.message.edit_text(text='Выберите продукт:',
                                         reply_markup=Keyboards.get_product(subcategory_id=callback_data['id']))
    await callback.answer()


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(product_catalog_callback_query)
    dispatcher.register_callback_query_handler(product_subcatalog_callback_query)
    dispatcher.register_callback_query_handler(products_callback_query)