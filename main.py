import logging
import asyncio
from flask import Flask
from bot import dp, bot
import handlers  # noqa: F401 - чтобы загрузились обработчики

logging.basicConfig(level=logging.INFO)

# Создаём Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())  # Запуск бота как асинхронную задачу
    app.run(host="0.0.0.0", port=8000)
    
