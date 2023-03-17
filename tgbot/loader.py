from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from os import getenv
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


bot = Bot(token=getenv('BOT_TOKEN_API'))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
