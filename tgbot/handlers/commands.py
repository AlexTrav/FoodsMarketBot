from aiogram import types, Dispatcher

from tgbot.loader import dp, bot

from tgbot.classes.states import UserStatesGroup
from tgbot.classes.keyboards import Keyboards

from tgbot.db.database import db


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message) -> None:
    db.check_user(user_id=message.from_user.id)
    await message.delete()
    await UserStatesGroup.start.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать в FoodsMarket!',
                           reply_markup=Keyboards.get_start_ikm())


@dp.message_handler(commands=['my_balance'], state='*')
async def my_balance_command(message: types.Message) -> None:
    await message.delete()
    text, keyboard = Keyboards.get_balance_user(user_id=message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id,
                           text=text,
                           reply_markup=keyboard)


@dp.message_handler(commands=['add_balance'], state='*')
async def add_balance_command(message: types.Message) -> None:
    await message.delete()
    text, keyboard = Keyboards.add_balance_user(user_id=message.from_user.id)
    await bot.send_message(chat_id=message.from_user.id,
                           text=text,
                           reply_markup=keyboard)


@dp.message_handler(commands=['set_address'], state='*')
async def pred_set_address_command(message: types.Message) -> None:
    await message.delete()
    await UserStatesGroup.add_address.set()
    text, keyboard = Keyboards.set_address_user(user_id=message.from_user.id, pos=0)
    await bot.send_message(chat_id=message.from_user.id,
                           text=text,
                           reply_markup=keyboard)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start_command, commands=['start'])
    dispatcher.register_message_handler(my_balance_command, commands=['my_balance'])
    dispatcher.register_message_handler(add_balance_command, commands=['add_balance'])
    dispatcher.register_message_handler(pred_set_address_command, commands=['set_address'])
