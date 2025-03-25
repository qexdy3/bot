from aiogram import types
from aiogram.filters import Command
from bot import dp
import bot
from config import CITIES, PRODUCTS, PRICES, CONTACTS_MASSAGE, START_MASSAGE, WORK_MASSAGE, LAW_MASSAGE, PRODUCT_MASSAGE
from keyboards import main_menu, city_selection, district_selection, product_selection, payment_button
from payment import create_crypto_invoice
from datetime import datetime, timedelta
import logging
from csv_data import load_csv_from_r2, save_csv_to_r2
from payment import check_payment_status
import asyncio
import random
import string

CSV_FILE = "users.csv"
ORDER_FILE = "orders.csv"
PENDING_INVOICES_FILE = "pending_invoices.csv"


def save_user(user_id, name, username):
    users = load_csv_from_r2(CSV_FILE)
    users = [row for row in users if row]  # Убираем пустые строки

    user_exists = any(str(row[0]) == str(user_id) for row in users)

    if not user_exists:
        reg_date = datetime.now().strftime("%Y-%m-%d")
        users.append([user_id, name, username, reg_date, 0, 0])
        save_csv_to_r2(CSV_FILE, users)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username if message.from_user.username else "Нет"
    
    save_user(user_id, name, username)
    
    await message.answer(START_MASSAGE, reply_markup=main_menu())

@dp.message(lambda message: message.text == "🚬 Купить 🚬")
async def handle_buy_text(message: types.Message):
    await message.answer(f"🇰🇬 Мы работаем только в Кыргызстане\n\n⤵️ Выбери город:", reply_markup=city_selection())

@dp.message(lambda message: message.text == "🚨 Контакты")
async def handle_contact_text(message: types.Message):
    await message.answer(CONTACTS_MASSAGE)

@dp.message(lambda message: message.text == "Работа 😎")
async def handle_contact_text(message: types.Message):
    await message.answer(WORK_MASSAGE)

@dp.message(lambda message: message.text == "Правила 📚")
async def handle_contact_text(message: types.Message):
    await message.answer(LAW_MASSAGE)

@dp.message(lambda message: message.text == "✅ Наличие товара по районам ✅")
async def handle_contact_text(message: types.Message):
    await message.answer(PRODUCT_MASSAGE)

@dp.message(lambda message: message.text == "⌛️ История заказов")
async def handle_order_text(message: types.Message):
    try:
        user_id = str(message.from_user.id)  # ID текущего пользователя
        current_time = datetime.now()
        updated_orders = []
        valid_orders = []
        
        orders = load_csv_from_r2(ORDER_FILE)
        if not orders:
            await message.answer("Заказы отсутствуют.")
            return
        
        headers = orders[0]  # Заголовки CSV
        changed = False  # Флаг для проверки изменений в списке заказов

        for row in orders[1:]:  # Пропускаем заголовки
            order_number, order_user_id, city, district, product, price, status, order_time = row

            # Проверяем, принадлежит ли заказ текущему пользователю
            if order_user_id != user_id:
                updated_orders.append(row)  # Оставляем чужие заказы
                continue  # Пропускаем этот заказ

            order_time = datetime.strptime(order_time, "%Y-%m-%d %H:%M:%S")

            # Удаляем заказы, которым больше часа
            if status == "Ожидает оплаты" and (current_time - order_time).total_seconds() > 3600:
                changed = True
                continue  # Пропускаем этот заказ
            
            updated_orders.append(row)

            order_text = (f"🛒 Номер заказа: #{order_number}\n\n"
                          f"🏙 Город: {city}\n"
                          f"📍 Район: {district}\n\n"
                          f"🚬 Вы выбрали товар: {product}\n\n"
                          f"💸 Цена: {price} USDT\n\n"
                          f"⏳ Время заказа: {order_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                          f"📌 Статус заказа: {status}\n")
            valid_orders.append(order_text)
        
        # Если были удаленные заказы, обновляем файл
        if changed:
            save_csv_to_r2(ORDER_FILE, [headers] + updated_orders)

        # Отправляем пользователю только его заказы
        if valid_orders:
            for order in valid_orders:
                await message.answer(order)
        else:
            await message.answer("У вас нет активных заказов.")
    except Exception as e:
        await message.answer("Ошибка при получении истории заказов.")
        print(f"Ошибка при чтении истории заказов: {e}")




@dp.message(lambda message: message.text == "Профиль 🥷")
async def handle_profile_text(message: types.Message):
    user_id = message.from_user.id
    users = load_csv_from_r2(CSV_FILE)

    for row in users:
        if row and str(row[0]) == str(user_id):
            profile_text = (f"ℹ️ Профиль\n\n"
                            f"❤️ Имя: {row[1]}\n"
                            f"😎 Юзер: @{row[2] if row[2] != 'Нет' else 'Без имени'}\n"
                            f"🔑 ID: {row[0]}\n"
                            f"🆕 Дата регистрации: {row[3]}\n"
                            f"🛒 Количество покупок: {row[4]}\n"
                            f"💰 Сумма покупок: {row[5]} $")
            await message.answer(profile_text)
            return
    
    await message.answer("Ваш профиль не найден.")


@dp.callback_query(lambda c: c.data.startswith("city_"))
async def choose_district(callback: types.CallbackQuery):
    city = callback.data.split("_")[1]
    await callback.message.edit_text(
        f"🌆 Город: {city}.\n\n🌃 Теперь выберите район:",
        reply_markup=district_selection(city)
    )

@dp.callback_query(lambda c: c.data.startswith("district_"))
async def choose_product(callback: types.CallbackQuery):
    district = callback.data.split("_")[1]
    city = callback.message.text.split("\n")[0].replace("\ud83c\udf06 Город: ", "")
    
    await callback.message.edit_text(
        f"{city}\n\n🌃 Район: {district}.\n\n🚬 Теперь выберите товар:",
        reply_markup=product_selection(district, PRODUCTS, PRICES)
    )


def get_invoice_by_order_id(order_id):
    """Ищет инвойс с нужным order_id."""
    invoices = load_csv_from_r2(PENDING_INVOICES_FILE)
    
    for row in invoices:
        if row[1] == order_id:  # order_id находится во втором столбце (индекс 1)
            return row[0]  # Возвращаем invoice_id (первый столбец)
    
    return None  # Если не нашли, возвращаем None


def save_order(invoice_id, user_id, city, district, product, price, status="Ожидает оплаты"):
    orders = load_csv_from_r2(ORDER_FILE)
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orders.append([invoice_id, user_id, city, district, product, price, status, order_time])
    save_csv_to_r2(ORDER_FILE, orders)


def generate_random_id(length=10):
    """Генерирует случайный ID заданной длины."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@dp.callback_query(lambda c: c.data.startswith("product_"))
async def confirm_purchase(callback: types.CallbackQuery):
    product = callback.data.split("_")[1]
    price = PRICES.get(product)
    
    if not price:
        await callback.message.edit_text("Ошибка: Товар не найден.")
        return
    
    city = callback.message.text.split("\n")[0].replace("\ud83c\udf06 Город: ", "")
    district = callback.message.text.split("\n")[2].replace("\ud83c\udf03 Район: ", "")

    order_id = generate_random_id()
    
    pay_url = create_crypto_invoice(price, callback.from_user.id, order_id)
    
    invoice_id = get_invoice_by_order_id(order_id)
    if not invoice_id:
        await callback.message.edit_text("Ошибка: Нет доступного инвойса для вашего заказа. Попробуйте позже.")
        return

    
    save_order(invoice_id, callback.from_user.id, city, district, product, price, status="Ожидает оплаты")
    
    text = (f"\U0001F6D2 Номер заказа: #{invoice_id}\n\n"
            f"{city}\n"
            f"{district}\n\n"
            f"\U0001F6AC Вы выбрали товар: {product}.\n\n"
            f"\U0001F4B8 Цена: {price} USDT.\n\n"
            f"\U0001F551 Время заказа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"\U0001F4CD Статус заказа: Ожидает оплаты\n\n"
            f"⏳ Нажмите кнопку ниже для оплаты:")
    
    await callback.message.edit_text(text, reply_markup=payment_button(pay_url))


# Обработчик кнопки "Назад" на уровне выбора города (возвращает в главное меню)
@dp.callback_query(lambda c: c.data == "back_start")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()  # Удаляем старое сообщение с inline-кнопками
    await callback.message.answer(START_MASSAGE, reply_markup=main_menu())  # Отправляем новое сообщение


# Обработчик кнопки "Назад" на уровне выбора района (возвращает на выбор города)
@dp.callback_query(lambda c: c.data.startswith("back_to_cities"))
async def back_to_cities(callback: types.CallbackQuery):
    await callback.message.edit_text("🇰🇬 Мы работаем только в Кыргызстане\n\n⤵️ Выбери город:", reply_markup=city_selection())

# Обработчик кнопки "Назад" на уровне выбора товаров (возвращает на выбор района)
@dp.callback_query(lambda c: c.data == "back_to_districts")
async def back_to_districts(callback: types.CallbackQuery):
    await callback.message.edit_text("🇰🇬 Мы работаем только в Кыргызстане\n\n⤵️ Выбери город:", reply_markup=city_selection())

async def monitor_invoices():
    while True:
        orders = load_csv_from_r2(ORDER_FILE)
        now = datetime.now()
        
        for order in orders:
            invoice_id, user_id, city, district, product, price, status, order_time = order
            order_datetime = datetime.strptime(order_time, "%Y-%m-%d %H:%M:%S")
            
            # Проверяем только ордера, которым меньше часа
            if status == "Ожидает оплаты" and now - order_datetime < timedelta(hours=1):
                paid = await check_payment_status(invoice_id, user_id, float(price))
                if paid:
                    order[6] = "✅ Оплачено"
                    save_csv_to_r2(ORDER_FILE, orders)
                    
                    # Отправляем сообщение пользователю
                    text = (f"✅ Ваш заказ #{invoice_id} оплачен!\n\n"
                            f"🏙 Город: {city}\n"
                            f"📍 Район: {district}\n"
                            f"🛒 Товар: {product}\n"
                            f"💰 Цена: {price} USDT\n"
                            f"🕒 Время заказа: {order_time}\n"
                            f"📌 Спасибо за покупку!")
                    
                    try:
                        await bot.send_message(user_id, text)
                    except Exception as e:
                        logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
        
        await asyncio.sleep(30)  # Проверка каждые 30 секунд
