from aiogram import executor
from tgbot.loader import dp
from tgbot.handlers import commands, message, callback_query


commands.register_handlers(dispatcher=dp)
message.register_handlers(dispatcher=dp)
callback_query.register_handlers(dispatcher=dp)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
    