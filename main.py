import subprocess
import time
import asyncio
import logging
from aiohttp import web
from bot import dp, bot
import handlers  # noqa: F401 - чтобы загрузились обработчики

URL = "https://awake-yolanthe-qexdy3-f008b061.koyeb.app/"

async def check_url():
    """Функция для проверки доступности URL."""
    while True:
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", URL], 
                capture_output=True, 
                text=True
            )
            status = result.stdout.strip()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Статус код: {status}")
        except Exception as e:
            print(f"Ошибка: {e}")

        await asyncio.sleep(120)  # Ожидание 2 минуты

async def handle(request):
    """Ответ сервера на запросы."""
    return web.Response(text="Сервер работает!")

async def web_server():
    """Создание и запуск веб-сервера."""
    app = web.Application()
    app.router.add_get("/", handle)
    return app

async def start_bot():
    """Запуск бота."""
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

async def main():
    """Запуск всех компонентов: веб-сервера, проверки URL и бота."""
    asyncio.create_task(check_url())  # Запускаем проверку URL

    # Запускаем веб-сервер
    app = await web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("Веб-сервер запущен на порту 8080...")

    # Запускаем бота
    await start_bot()

# Запуск асинхронного кода
asyncio.run(main())
