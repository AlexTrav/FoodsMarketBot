from aiogram import Bot, Dispatcher, executor, types

from aiogram.utils.callback_data import CallbackData

# from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher.filters.state import State
from classes.states import UserStatesGroup

# from db.database import db

from variables.config import get_token_api

from classes.keyboards import Keyboards


bot = Bot(token=get_token_api())
dp = Dispatcher(bot=bot, storage=MemoryStorage())


# Commands-handlers:
@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message) -> None:
    await message.delete()
    await UserStatesGroup.start.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать в FoodsMarket!',
                           reply_markup=Keyboards.get_start_ikm())


# Callback-query handlers:
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
        await UserStatesGroup.product_subcatalog.set()
        await callback.message.edit_text(text='Выберите продукт:',
                                         reply_markup=Keyboards.get_product(subcategory_id=callback_data['id']))
    await callback.answer()


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
