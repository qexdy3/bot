import requests
import asyncio
import aiohttp
import logging
from aiogram import Bot
from config import CRYPTOBOT_TOKEN
from csv_data import load_csv_from_r2, save_csv_to_r2

ORDER_FILE = "orders.csv"
USER_PURCHASES_FILE = "users.csv"
INVOICE_FILE = "pending_invoices.csv"

def load_invoices():
    """Загружает список неоплаченных инвойсов из CSV."""
    try:
        return {row[0]: (row[1], row[2] , float(row[3])) for row in load_csv_from_r2(INVOICE_FILE) if row}
    except Exception as e:
        logging.error(f"Ошибка при загрузке инвойсов: {e}")
        return {}

def save_invoices(invoices):
    """Сохраняет список неоплаченных инвойсов в CSV."""
    data = [[invoice_id, order_id, user_id, amount] for invoice_id, (order_id, user_id, amount) in invoices.items()]
    save_csv_to_r2(INVOICE_FILE, data)

def update_csv(user_id, amount):
    users = load_csv_from_r2(USER_PURCHASES_FILE)
    updated_users = []
    found = False
    
    for row in users:
        if row and row[0] == str(user_id):
            row[-2] = str(int(row[-2]) + 1)  # Количество покупок
            row[-1] = str(float(row[-1]) + amount)  # Сумма покупок
            found = True
        updated_users.append(row)
    
    if not found:
        updated_users.append([user_id, "Unknown", "Unknown", "Unknown", "1", str(amount)])
    
    save_csv_to_r2(USER_PURCHASES_FILE, updated_users)

def update_order_status(user_id, amount, status="Оплачено"):
    orders = load_csv_from_r2(ORDER_FILE)
    updated_orders = []
    
    for row in orders:
        if row[1] == str(user_id) and row[5] == str(amount) and row[6] == "Ожидает оплаты":
            row[6] = status  # Обновляем статус заказа
        updated_orders.append(row)
    
    save_csv_to_r2(ORDER_FILE, updated_orders)

def create_crypto_invoice(amount, user_id, order_id):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    data = {
        "asset": "USDT",
        "amount": amount,
        "description": "Оплата заказа в магазине",
        "hidden_message": f"Оплата заказа для пользователя {user_id}",
        "payload": str(user_id),
        "paid_btn_name": "viewItem",
        "paid_btn_url": "https://t.me/Kkraken_shop_bot"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data).json()
        if response.get("ok"):
            invoice_id = response["result"]["invoice_id"]
            pending_invoices = load_invoices()
            pending_invoices[invoice_id] = (order_id ,user_id, amount)
            save_invoices(pending_invoices)
            return response["result"]["pay_url"]
        else:
            return "https://t.me/Kkraken_shop_bot"
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при создании инвойса: {e}")
        return "https://t.me/Kkraken_shop_bot"

async def check_payment_status(invoice_id: str, user_id: str, amount: float) -> bool:
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    params = {"invoice_ids": invoice_id}  # Проверяем только указанный invoice_id

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                response = await resp.json()

                if response.get("ok"):
                    invoices = response.get("result", {}).get("items", [])
                    
                    # Ищем нужный invoice_id
                    for invoice in invoices:
                        if str(invoice.get("invoice_id")) == str(invoice_id):  # Проверка конкретного инвойса
                            if invoice.get("status") == "paid":
                                update_order_status(user_id, amount)
                                update_csv(user_id, amount)
                                return True
    except Exception as e:
        logging.error(f"Ошибка при проверке статуса: {e}")
    return False


