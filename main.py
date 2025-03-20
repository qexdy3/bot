import asyncio
import logging
import signal
from bot import dp, bot
import handlers  # noqa: F401 - загружаем обработчики

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Обрабатываем сигналы завершения (чтобы бот корректно закрывался)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(dp.stop_polling()))

    await dp.start_polling(bot)  # Правильный запуск в aiogram 3

if __name__ == "__main__":
    asyncio.run(main())
