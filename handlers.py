from aiogram import types
from aiogram.filters import Command
from bot import dp
from config import CITIES, PRODUCTS, PRICES, CONTACTS_MASSAGE, START_MASSAGE, WORK_MASSAGE, LAW_MASSAGE, PRODUCT_MASSAGE
from keyboards import main_menu, city_selection, district_selection, product_selection, payment_button
from payment import create_crypto_invoice
import csv
import os
from datetime import datetime

CSV_FILE = "users.csv"
ORDER_FILE = "orders.csv"

def save_user(user_id, name, username):
    user_exists = False
    reg_date = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            users = list(reader)
            for user in users:
                if user and str(user[0]) == str(user_id):
                    user_exists = True
                    break
    
    if not user_exists:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, name, username, reg_date, 0, 0])

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
        current_time = datetime.now()
        updated_orders = []
        valid_orders = []
        
        with open(ORDER_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            for row in reader:
                order_number = row[0]
                user_id = row[1]
                city = row[2]
                district = row[3]
                product = row[4]
                price = row[5]
                status = row[6]
                order_time = datetime.strptime(row[7], "%Y-%m-%d %H:%M:%S")
                
                # Если заказ старше 1 часа и статус "Ожидает оплаты", пропускаем его (не добавляем в обновленный список)
                if status == "Ожидает оплаты" and (current_time - order_time).total_seconds() > 3600:
                    continue
                
                updated_orders.append(row)
                
                order_text = (f"🛒 Номер заказа: #300{order_number}\n\n"
                              f"👤 ID пользователя: {user_id}\n"
                              f"{city}\n"
                              f"{district}\n\n"
                              f"🚬 Вы выбрали товар: {product}\n\n"
                              f"💸 Цена: {price} USDT\n\n"
                              f"⏳ Время заказа: {order_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                              f"📌 Статус заказа: {status}\n")
                valid_orders.append(order_text)
        
        # Перезаписываем CSV-файл, оставляя только актуальные заказы
        with open(ORDER_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(updated_orders)
        
        if valid_orders:
            for order in valid_orders:
                await message.answer(order)
        else:
            await message.answer("Заказы отсутствуют.")
    except Exception as e:
        await message.answer("Ошибка при получении истории заказов.")
        print(f"Ошибка при чтении истории заказов: {e}")


@dp.message(lambda message: message.text == "Профиль 🥷")
async def handle_profile_text(message: types.Message):
    user_id = message.from_user.id
    
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
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

def generate_order_number():
    if not os.path.exists(ORDER_FILE):
        return 1
    
    with open(ORDER_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        orders = list(reader)
    
    return len(orders) + 1 if orders else 1

# Функция для сохранения заказа
def save_order(order_number, user_id, city, district, product, price, status="Ожидает оплаты"):
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ORDER_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([order_number, user_id, city, district, product, price, status, order_time])

@dp.callback_query(lambda c: c.data.startswith("product_"))
async def confirm_purchase(callback: types.CallbackQuery):
    product = callback.data.split("_")[1]
    price = PRICES.get(product)
    
    if not price:
        await callback.message.edit_text("Ошибка: Товар не найден.")
        return
    
    city = callback.message.text.split("\n")[0].replace("\ud83c\udf06 Город: ", "")
    district = callback.message.text.split("\n")[2].replace("\ud83c\udf03 Район: ", "")
    
    order_number = generate_order_number()
    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_order(order_number, callback.from_user.id, city, district, product, price, status="Ожидает оплаты")
    
    pay_url = create_crypto_invoice(price, callback.from_user.id, order_number)
    
    text = (f"🛒 Номер заказа: #300{order_number}\n\n"
            f"{city}\n"
            f"{district}\n\n"
            f"🚬 Вы выбрали товар: {product}.\n\n"
            f"💸 Цена: {price} USDT.\n\n"
            f"🕒 Время заказа: {order_time}\n\n"
            f"📌 Статус заказа: Ожидает оплаты\n\n"
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
