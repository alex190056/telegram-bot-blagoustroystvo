import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ================== Настройки ==================
API_TOKEN = os.environ.get("7914401034:AAHwS6HEGkpfd0p2-QKsk_zLaXWUtZrOk3o")  # токен бота из переменных окружения
ADMIN_ID = int(os.environ.get("281389805", 0))  # твой Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== Главное меню ==================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏗 Услуги"), KeyboardButton(text="💰 Цены")],
        [KeyboardButton(text="🚚 Материалы"), KeyboardButton(text="🧮 Калькулятор")],
        [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="📝 Заявка")]
    ],
    resize_keyboard=True
)

# ================== FSM ==================
class RequestForm(StatesGroup):
    service = State()
    address = State()
    area = State()
    phone = State()

class CalcForm(StatesGroup):
    service = State()
    area = State()

# ================== Цены услуг ==================
service_prices = {
    "Асфальт": 500,
    "Плитка": 1200,
    "Бордюры": 300
}

material_prices = {
    "Щебень": 1000,
    "ПГС": 800,
    "Песок": 500
}

# ================== /start ==================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать!\n"
        "Благоустройство территорий: асфальт, плитка, бордюры\n"
        "Выберите раздел👇",
        reply_markup=main_kb
    )

# ================== Услуги ==================
@dp.message(lambda m: m.text == "🏗 Услуги")
async def services(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Асфальт"), KeyboardButton(text="Плитка")],
            [KeyboardButton(text="Бордюры"), KeyboardButton(text="⬅ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите услугу:", reply_markup=kb)

@dp.message(lambda m: m.text in ["Асфальт", "Плитка", "Бордюры"])
async def show_service(message: types.Message):
    descriptions = {
        "Асфальт": "Асфальтирование дорог и площадок 🚧",
        "Плитка": "Укладка тротуарной плитки 🧱",
        "Бордюры": "Установка бордюров"
    }
    await message.answer(descriptions[message.text])

@dp.message(lambda m: m.text == "⬅ Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_kb)

# ================== Цены ==================
@dp.message(lambda m: m.text == "💰 Цены")
async def prices(message: types.Message):
    text = "\n".join([f"{k} — {v} ₽/м²" for k, v in service_prices.items()])
    await message.answer(f"💰 Цены:\n{text}")

# ================== Материалы ==================
@dp.message(lambda m: m.text == "🚚 Материалы")
async def materials(message: types.Message):
    text = "\n".join([f"{k} — {v} ₽/т" for k, v in material_prices.items()])
    await message.answer(f"🚚 Материалы:\n{text}\nДоставка есть 🚛")

# ================== Контакты ==================
@dp.message(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "📞 Контакты:\n\n"
        "Имя: Александр Геворкян\n"
        "Телефон: +7 932 552 0104\n"
        "Email: drofa528@bk.ru",
        reply_markup=contact_kb
    )

# ================== Калькулятор ==================
@dp.message(lambda m: m.text == "🧮 Калькулятор")
async def calc_start(message: types.Message, state: FSMContext):
    await message.answer("Введите услугу (Асфальт / Плитка / Бордюры):")
    await state.set_state(CalcForm.service)

@dp.message(CalcForm.service)
async def calc_service(message: types.Message, state: FSMContext):
    service = message.text
    if service not in service_prices:
        await message.answer("⚠ Неверная услуга. Попробуйте ещё раз.")
        return
    await state.update_data(service=service)
    await message.answer("Введите площадь (м²):")
    await state.set_state(CalcForm.area)

@dp.message(CalcForm.area)
async def calc_area(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service = data["service"]

    try:
        area = float(message.text)
    except ValueError:
        await message.answer("Введите число!")
        return

    total = area * service_prices[service]
    await message.answer(f"💰 Стоимость услуги {service} на {area} м²: {int(total)} ₽")
    await state.clear()

# ================== Заявка ==================
@dp.message(lambda m: m.text == "📝 Заявка")
async def request_start(message: types.Message, state: FSMContext):
    await message.answer("Что вам нужно?")
    await state.set_state(RequestForm.service)

@dp.message(RequestForm.service)
async def req_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer("Адрес:")
    await state.set_state(RequestForm.address)

@dp.message(RequestForm.address)
async def req_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Площадь:")
    await state.set_state(RequestForm.area)

@dp.message(RequestForm.area)
async def req_area(message: types.Message, state: FSMContext):
    await state.update_data(area=message.text)
    await message.answer("Телефон:")
    await state.set_state(RequestForm.phone)

@dp.message(RequestForm.phone)
async def req_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = (
        f"📩 Новая заявка:\nУслуга: {data['service']}\n"
        f"Адрес: {data['address']}\nПлощадь: {data['area']}\n"
        f"Телефон: {message.text}"
    )
    await bot.send_message(ADMIN_ID, text)
    await message.answer("✅ Заявка отправлена!")
    await state.clear()

# ================== Запуск ==================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())