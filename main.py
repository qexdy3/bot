import logging
import asyncio
from bot import dp, bot, web_server
import handlers  # noqa: F401 - чтобы загрузились обработчики
from aiohttp import web

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Запускаем веб-сервер
    app = await web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)  # Сервер будет слушать все IP на порту 8080
    await site.start()
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
