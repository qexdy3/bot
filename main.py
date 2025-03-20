import logging
import threading
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

# Функция для запуска бота в отдельном потоке
def start_bot():
    dp.run_polling(bot)

# Запускаем бота в фоновом режиме
threading.Thread(target=start_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    
