import logging
from bot import dp, bot
import handlers  # noqa: F401 - чтобы загрузились обработчики

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)
