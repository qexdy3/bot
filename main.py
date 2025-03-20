import logging
import asyncio
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot import bot, dp

# Получаем URL сервера
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Настраиваем FastAPI
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

# Обработчик запросов Telegram
async def telegram_webhook(request: Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"status": "ok"}

# Подключаем обработчик
app.post("/webhook")(telegram_webhook)

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
