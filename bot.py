from aiogram import Bot, Dispatcher, executor

# from db.database import db
from variables.config import TOKEN_API

bot = Bot(token=TOKEN_API)
dp = Dispatcher(bot=bot)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
