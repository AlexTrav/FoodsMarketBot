from aiogram import types, Dispatcher

from tgbot.loader import dp, bot

from tgbot.classes.states import UserStatesGroup
from tgbot.classes.keyboards import Keyboards


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message) -> None:
    await message.delete()
    await UserStatesGroup.start.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать в FoodsMarket!',
                           reply_markup=Keyboards.get_start_ikm())


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start_command, commands=['start'])
