from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Простое хранилище состояний
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())  # Добавляем хранилище
