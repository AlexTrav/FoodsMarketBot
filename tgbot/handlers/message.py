from aiogram import types, Dispatcher

from tgbot.loader import dp, bot

from tgbot.classes.states import UserStatesGroup
from tgbot.classes.keyboards import Keyboards

from aiogram.dispatcher import FSMContext


@dp.message_handler(content_types=['text'], state=UserStatesGroup.add_address)
async def set_address_message(message: types.Message, state: FSMContext) -> None:
    if await state.get_state() == 'UserStatesGroup:add_address':
        await message.delete()
        text, keyboard = Keyboards.set_address_user(user_id=message.from_user.id, address=message.text, pos=1)
        await bot.send_message(chat_id=message.from_user.id,
                               text=text,
                               reply_markup=keyboard)


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(set_address_message)
