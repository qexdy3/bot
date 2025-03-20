import requests
import csv
from config import CRYPTOBOT_TOKEN


ORDER_FILE = "orders.csv"

def update_csv(user_id, amount):
    file_path = "user_purchases.csv"
    updated_rows = []
    found = False
    
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == str(user_id):
                    row[-2] = str(int(row[-2]) + 1)  # Количество покупок
                    row[-1] = str(float(row[-1]) + amount)  # Сумма покупок
                    found = True
                updated_rows.append(row)
    except FileNotFoundError:
        pass
    
    if not found:
        updated_rows.append([user_id, "Unknown", "Unknown", "Unknown", "1", str(amount)])
    
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)


def update_order_status(user_id, amount, status="Оплачено"):
    orders = []
    with open(ORDER_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == str(user_id) and row[5] == str(amount) and row[6] == "Ожидает оплаты":
                row[6] = status  # Обновляем статус заказа
            orders.append(row)
    
    with open(ORDER_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(orders)

def create_crypto_invoice(amount, user_id, id_order):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    data = {
        "asset": "USDC",
        "amount": amount,
        "description": "Оплата заказа в магазине",
        "hidden_message": f"Оплата заказа для пользователя {user_id}",
        "payload": str(user_id),
        "paid_btn_name": "viewItem",
        "paid_btn_url": "https://t.me/Kkraken_shop_bot"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data).json()
        return response["result"]["pay_url"] if response.get("ok") else "https://t.me/Kkraken_shop_bot"
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании инвойса: {e}")
        return "https://t.me/Kkraken_shop_bot"

async def check_payment_status(invoice_id: str, user_id: str, amount: float) -> bool:
    url = "https://pay.crypt.bot/api/getInvoiceStatus"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN}
    data = {"invoice_id": invoice_id}
    
    try:
        response = requests.post(url, headers=headers, json=data).json()
        if response.get("ok") and response["result"].get("status") == "paid":
            update_order_status(user_id, amount)
            return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при проверке статуса: {e}")
    return False
