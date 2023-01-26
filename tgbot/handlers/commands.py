from aiogram import types, Dispatcher

from tgbot.loader import dp, bot

from tgbot.classes.states import UserStatesGroup, CourierStatesGroup, OperatorStatesGroup  # , AdminStatesGroup
from tgbot.classes.keyboards import Keyboards

from tgbot.db.database import db


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message) -> None:
    db.check_user(user_id=message.from_user.id)
    role_id = db.get_role_id(user_id=message.from_user.id)
    await message.delete()
    ###################################USER###################################
    if role_id == 1:
        await UserStatesGroup.start.set()
        await bot.send_message(chat_id=message.from_user.id,
                               text='Добро пожаловать в FoodsMarket!',
                               reply_markup=Keyboards.get_start_ikm())
    ##################################OPERATOR################################
    elif role_id == 2:
        await OperatorStatesGroup.start.set()
        await bot.send_message(chat_id=message.from_user.id,
                               text='Оператор! Добро пожаловать в FoodsMarket!',
                               reply_markup=Keyboards.get_start_operator())
    ##################################COURIER#################################
    elif role_id == 3:
        await CourierStatesGroup.start.set()
        await bot.send_message(chat_id=message.from_user.id,
                               text='Курьер! Добро пожаловать в FoodsMarket!',
                               reply_markup=Keyboards.get_start_courier())
    ##################################ADMIN###################################
    elif role_id == 4:
        pass


###################################################################REGISTER_HANDLERS##################################################################################

def register_handlers(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start_command, commands=['start'])

