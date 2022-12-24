from aiogram import types, Dispatcher

from tgbot.loader import dp

from tgbot.classes.states import UserStatesGroup
from tgbot.classes.keyboards import Keyboards

from aiogram.dispatcher import FSMContext


@dp.message_handler(content_types=['text'], state=UserStatesGroup.add_address)
async def set_address_message(message: types.Message, state: FSMContext) -> None:
    if await state.get_state() == 'UserStatesGroup:add_address':
        await UserStatesGroup.my_profile.set()
        Keyboards.set_address_user(user_id=message.from_user.id, pos=1, address=message.text)
        await message.delete()
        text, keyboard = Keyboards.get_profile(user_id=message.from_user.id)
        await message.answer(text=text,
                             reply_markup=keyboard,
                             parse_mode='HTML')


@dp.message_handler(content_types=['text'], state=UserStatesGroup.add_phone)
async def set_phone_message(message: types.Message, state: FSMContext) -> None:
    if await state.get_state() == 'UserStatesGroup:add_phone':
        await UserStatesGroup.my_profile.set()
        Keyboards.set_phone_user(user_id=message.from_user.id, pos=1, phone=message.text)
        await message.delete()
        text, keyboard = Keyboards.get_profile(user_id=message.from_user.id)
        await message.answer(text=text,
                             reply_markup=keyboard,
                             parse_mode='HTML')


def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(set_address_message)
    dispatcher.register_message_handler(set_phone_message)
