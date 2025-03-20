from aiogram import Bot, Dispatcher
from aiohttp import web
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def handle_root(request):
    return web.Response(text="Бот работает!")

async def get_status(request):
    return web.json_response({"status": "running", "bot_id": (await bot.me()).id})

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/status", get_status)
    return app
