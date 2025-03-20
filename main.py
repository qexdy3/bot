import logging
import asyncio
from bot import dp, bot
import handlers  # noqa: F401 - чтобы загрузились обработчики
from flask import Flask

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаем Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_bot())  # Запуск бота в асинхронной задаче
    app.run(host="0.0.0.0", port=8000)
    
