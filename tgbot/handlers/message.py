from aiogram import types, Dispatcher

from tgbot.loader import dp

from tgbot.classes.states import UserStatesGroup, OperatorStatesGroup, AdminStatesGroup
from tgbot.classes.keyboards import Keyboards

from aiogram.dispatcher import FSMContext


#######################################################################USER#########################################################################################

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


@dp.message_handler(content_types=['text'], state=UserStatesGroup.search)
async def search_results_message(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    async with state.proxy() as data:
        data['search_query'] = message.text
    text, keyboard = Keyboards.get_search_products(search_query=message.text)
    await message.answer(text=text,
                         reply_markup=keyboard)

#######################################################################OPERATOR#######################################################################################

@dp.message_handler(content_types=['text'], state=OperatorStatesGroup.search)
async def search_results_message(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    async with state.proxy() as data:
        data['back_id'] = 1
        data['search_query'] = message.text
    text, keyboard = Keyboards.get_search_products(search_query=message.text)
    await message.answer(text=text,
                         reply_markup=keyboard)


@dp.message_handler(content_types=['text'], state=OperatorStatesGroup.search_id)
async def search_id_results_message(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    async with state.proxy() as data:
        data['back_id'] = 2
        data['search_id'] = message.text
    if message.text.isdigit():
        text, keyboard = Keyboards.get_search_id_product(search_id=message.text)
        await message.answer(text=text,
                             reply_markup=keyboard)
    else:
        await message.reply('Это не цена!')


@dp.message_handler(content_types=['text'], state=OperatorStatesGroup.change_price)
async def change_price_product_message(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text.isdigit():
            await OperatorStatesGroup.product.set()
            Keyboards.set_new_price(message.text)
            await message.delete()
            text, keyboard, photo = Keyboards.get_product_operator(product_id=data['product_id'])
            await message.answer_photo(photo=photo,
                                       caption=text,
                                       reply_markup=keyboard)
        else:
            await message.reply('Это не цена!')


@dp.message_handler(content_types=['text'], state=OperatorStatesGroup.add_product)
async def add_product_message(message: types.Message):
    if message.text.count(';') == 5:
        answer = Keyboards.add_product(message.text)
        await message.answer(answer)
        if 'Продукт добавлен!' in answer:
            await OperatorStatesGroup.working_warehouse.set()
            text, keyboard = Keyboards.get_working_warehouse()
            await message.answer(text=text,
                                 reply_markup=keyboard)
        else:
            await OperatorStatesGroup.working_warehouse.set()
            text, keyboard = Keyboards.get_working_warehouse()
            await message.answer(text=text,
                                 reply_markup=keyboard)
    else:
        await message.answer('Не верный ввод! Должно быть 5 разделителей ;')
        await OperatorStatesGroup.working_warehouse.set()
        text, keyboard = Keyboards.get_working_warehouse()
        await message.answer(text=text,
                             reply_markup=keyboard)
    await message.delete()

#######################################################################ADMIN##########################################################################################

@dp.message_handler(content_types=['text'], state=AdminStatesGroup.give_role_user)
async def give_role_message(message: types.Message):
    if message.text.isdigit():
        if int(message.text) in Keyboards.get_users_table():
            text, keyboard = Keyboards.get_user_roles(user_id=message.text)
            await message.answer(text=text,
                                 reply_markup=keyboard)
        else:
            await message.answer('Такого кода нет в базе данных')
            text, keyboard = Keyboards.set_user_id()
            await message.answer(text=text,
                                 reply_markup=keyboard)
    else:
        await message.answer('Код должен быть числовым')
        text, keyboard = Keyboards.set_user_id()
        await message.answer(text=text,
                             reply_markup=keyboard)
    await message.delete()


@dp.message_handler(content_types=['text'], state=AdminStatesGroup.add_balance_user)
async def add_balance_message(message: types.Message):
    if message.text.isdigit():
        if int(message.text) in Keyboards.get_users_table():
            text, keyboard = Keyboards.get_user_inf(user_id=int(message.text))
            await message.answer(text=text,
                                 reply_markup=keyboard)
        else:
            await message.answer('Такого кода нет в базе данных')
            text, keyboard = Keyboards.set_user_id()
            await message.answer(text=text,
                                 reply_markup=keyboard)
    else:
        await message.answer('Код должен быть числовым')
        text, keyboard = Keyboards.set_user_id()
        await message.answer(text=text,
                             reply_markup=keyboard)
    await message.delete()

###################################################################REGISTER_HANDLERS##################################################################################

def register_handlers(dispatcher: Dispatcher):
    ###################################USER###################################
    dispatcher.register_message_handler(set_address_message)
    dispatcher.register_message_handler(set_phone_message)
    dispatcher.register_message_handler(search_results_message)
    ##################################OPERATOR################################
    dispatcher.register_message_handler(search_results_message)
    dispatcher.register_message_handler(search_id_results_message)
    dispatcher.register_message_handler(change_price_product_message)
    dispatcher.register_message_handler(add_product_message)
    ##################################ADMIN###################################
    dispatcher.register_message_handler(give_role_message)
    dispatcher.register_message_handler(add_balance_message)
