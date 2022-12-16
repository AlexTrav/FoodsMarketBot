from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tgbot.variables.config import get_token_api


bot = Bot(token=get_token_api())
dp = Dispatcher(bot=bot, storage=MemoryStorage())
