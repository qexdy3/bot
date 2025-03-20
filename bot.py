from aiogram import Bot, Dispatcher

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def on_startup():
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))

dp.startup.register(on_startup)
