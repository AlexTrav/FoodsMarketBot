from aiogram import types, Dispatcher

from tgbot.db.database import db
from tgbot.loader import dp

from tgbot.classes.states import UserStatesGroup, OperatorStatesGroup, AdminStatesGroup
from tgbot.classes.keyboards import Keyboards

from aiogram.types import ReplyKeyboardRemove

from aiogram.dispatcher import FSMContext

from tgbot.variables.config import Users, MainPage


#######################################################################USER#########################################################################################

@dp.message_handler(content_types=['text'], state=UserStatesGroup.add_address)
async def is_cancel_message(message: types.Message) -> None:
    if message.text == 'Отмена':
        await UserStatesGroup.my_profile.set()
        await message.delete()
        text, keyboard = Keyboards.get_profile(user_id=message.from_user.id)
        await message.answer(text="Изменения отменены", reply_markup=ReplyKeyboardRemove())
        await message.answer(text=text,
                             reply_markup=keyboard,
                             parse_mode='HTML')


@dp.message_handler(content_types=['location'], state=UserStatesGroup.add_address)
async def location(message):
    if message.location is not None:
        await UserStatesGroup.my_profile.set()
        address = f"{message.location['latitude']}, {message.location['longitude']}"
        Keyboards.set_address_user(user_id=message.from_user.id, pos=1, address=address)
        await message.delete()
        await message.answer(text="Изменения сохранены", reply_markup=ReplyKeyboardRemove())
        text, keyboard = Keyboards.get_profile(user_id=message.from_user.id)
        await message.answer(text=text,
                             reply_markup=keyboard,
                             parse_mode='HTML')


@dp.message_handler(content_types=['text'], state=UserStatesGroup.add_phone)
async def is_cancel_message(message: types.Message) -> None:
    if message.text == 'Отмена':
        await UserStatesGroup.my_profile.set()
        await message.delete()
        text, keyboard = Keyboards.get_profile(user_id=message.from_user.id)
        await message.answer(text="Изменения отменены", reply_markup=ReplyKeyboardRemove())
        await message.answer(text=text,
                             reply_markup=keyboard,
                             parse_mode='HTML')


@dp.message_handler(content_types=types.ContentType.CONTACT, state=UserStatesGroup.add_phone)
async def contacts(message: types.Message):
    await UserStatesGroup.my_profile.set()
    Keyboards.set_phone_user(user_id=message.from_user.id, phone_number=message.contact.phone_number)
    await message.delete()
    await message.answer(text="Изменения сохранены!", reply_markup=ReplyKeyboardRemove())
    text, keyboard = Keyboards.get_profile(user_id=message.from_user.id)
    await message.answer(text=text,
                         reply_markup=keyboard,
                         parse_mode='HTML')


@dp.message_handler(content_types=['text'], state=UserStatesGroup.search)
async def search_results_message(message: types.Message, state: FSMContext) -> None:
    await message.delete()
    async with state.proxy() as data:
        data['search_query'] = message.text
    MainPage.entries = 10
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
    MainPage.entries = 10
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
            text, keyboard, photo = Keyboards.get_product_operator(product_id=data['product_id'], state=OperatorStatesGroup.state)
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
    if message.text in Keyboards.get_usernames():
        user_id = Keyboards.get_user_id_for_username(message.text)
        text, keyboard = Keyboards.get_user_roles(user_id=user_id)
        await message.answer(text=text,
                             reply_markup=keyboard)
    else:
        await message.answer('Такого username-а нет в базе данных')
        text, keyboard = Keyboards.set_username()
        await message.answer(text=text,
                             reply_markup=keyboard)
    await message.delete()


@dp.message_handler(content_types=['text'], state=AdminStatesGroup.add_balance)
async def add_user_id_message(message: types.Message):
    if message.text in Keyboards.get_usernames():
        user_id = Keyboards.get_user_id_for_username(message.text)
        text, keyboard = Keyboards.get_user_inf(user_id=user_id)
        await message.answer(text=text,
                             reply_markup=keyboard,
                             parse_mode='HTML')
    else:
        await message.answer('Такого username-a нет в базе данных')
        text, keyboard = Keyboards.set_username()
        await message.answer(text=text,
                             reply_markup=keyboard)
    await message.delete()


@dp.message_handler(content_types=['text'], state=AdminStatesGroup.add_balance_user)
async def add_balance_message(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await AdminStatesGroup.add_balance.set()
        db.update_balance(sum=message.text, user_id=Users.id)
        async with state.proxy() as data:
            if data['back_id'] == 2:
                await AdminStatesGroup.document.set()
                Keyboards.get_update_documents_add_balance(message.from_user.id, int(message.text), data['document_id'])
                text, keyboard = Keyboards.get_document(data['document_id'])
                await message.answer(text=text,
                                     reply_markup=keyboard)
            else:
                Keyboards.get_insert_documents_add_balance(message.from_user.id, int(message.text))
                text, keyboard = Keyboards.get_user_inf(user_id=Users.id)
                await message.answer(text=text,
                                     reply_markup=keyboard,
                                     parse_mode='HTML')
        Users.id = ''
    else:
        await message.answer('Сумма должна быть числом')
    await message.delete()


###################################################################REGISTER_HANDLERS##################################################################################

def register_handlers(dispatcher: Dispatcher):
    ###################################USER###################################
    dispatcher.register_message_handler(location)
    dispatcher.register_message_handler(is_cancel_message)
    dispatcher.register_message_handler(contacts)
    dispatcher.register_message_handler(search_results_message)
    ##################################OPERATOR################################
    dispatcher.register_message_handler(search_results_message)
    dispatcher.register_message_handler(search_id_results_message)
    dispatcher.register_message_handler(change_price_product_message)
    dispatcher.register_message_handler(add_product_message)
    ##################################ADMIN###################################
    dispatcher.register_message_handler(give_role_message)
    dispatcher.register_message_handler(add_user_id_message)
    dispatcher.register_message_handler(add_balance_message)
