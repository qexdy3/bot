from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import CITIES

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚬 Купить 🚬"), KeyboardButton(text="Профиль 🥷")],
            [KeyboardButton(text="✅ Наличие товара по районам ✅")],
            [KeyboardButton(text="⌛️ История заказов"), KeyboardButton(text="Правила 📚")],
            [KeyboardButton(text="🚨 Контакты"), KeyboardButton(text="Работа 😎")]
        ],
        resize_keyboard=True
    )


def city_selection():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇰🇬 " + city + " 🇰🇬", callback_data=f"city_{city}")] for city in CITIES.keys()
    ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_start")]])

def district_selection(city):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇰🇬 " + district + " 🇰🇬", callback_data=f"district_{district}")] for district in CITIES.get(city, [])
    ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_cities_{city}")]])

def product_selection(district, products, prices):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{product} - {prices.get(product, 'Цена не указана')} USDT", callback_data=f"product_{product}")]
        for product in products.get(district, [])
    ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_districts")]])

def payment_button(pay_url):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="💸 Оплатить через CryptoBot 💸", url=pay_url)]])
