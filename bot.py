import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "7914401034:AAHwS6HEGkpfd0p2-QKsk_zLaXWUtZrOk3o"
ADMIN_ID = 281389805

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== КНОПКИ ==================
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

# ================== START ==================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Благоустройство территорий:\n"
        "асфальтирование, укладка плитки, установка бордюров\n\n"
        "Выберите раздел👇",
        reply_markup=main_kb
    )

# ================== УСЛУГИ ==================
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

@dp.message(lambda m: m.text == "Асфальт")
async def asfalt(message: types.Message):
    await message.answer("Асфальтирование дорог и площадок 🚧")

@dp.message(lambda m: m.text == "Плитка")
async def tile(message: types.Message):
    await message.answer("Укладка тротуарной плитки 🧱")

@dp.message(lambda m: m.text == "Бордюры")
async def bord(message: types.Message):
    await message.answer("Установка бордюров")

@dp.message(lambda m: m.text == "⬅ Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_kb)

# ================== ЦЕНЫ ==================
@dp.message(lambda m: m.text == "💰 Цены")
async def prices(message: types.Message):
    await message.answer(
        "💰 Цены:\n\n"
        "Асфальт — от 500 ₽/м²\n"
        "Плитка — от 1200 ₽/м²\n"
        "Бордюры — от 300 ₽/м.п."
    )

# ================== МАТЕРИАЛЫ ==================
@dp.message(lambda m: m.text == "🚚 Материалы")
async def materials(message: types.Message):
    await message.answer(
        "🚚 Материалы:\n\n"
        "Щебень — от 1500 ₽/т\n"
        "ПГС — от 1000 ₽/т\n"
        "Песок — от 800 ₽/т\n"
        "Доставка есть 🚛"
    )

# ================== КАЛЬКУЛЯТОР ==================
service_prices = {
    "Асфальт": 500,
    "Плитка": 1200,
    "Бордюры": 300
}

# Обработчик кнопки калькулятора
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

    # Рассчёт стоимости
    total = area * service_prices[service]

    await message.answer(f"💰 Стоимость услуги {service} на {area} м²: {int(total)} ₽")
    await state.clear()

# ================== ЗАЯВКА ==================
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
        "📩 Новая заявка:\n\n"
        f"Услуга: {data['service']}\n"
        f"Адрес: {data['address']}\n"
        f"Площадь: {data['area']}\n"
        f"Телефон: {message.text}"
    )

    await bot.send_message(ADMIN_ID, text)
    await message.answer("✅ Заявка отправлена!")
    await state.clear()


@dp.message(lambda m: m.text == "📞 Контакты")
async def contacts(message: types.Message):
    # Если хочешь прямо сделать кнопку звонка:
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Позвонить", request_contact=True)],
            [KeyboardButton(text="⬅ Назад")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "📞 Мои контакты:\n\n"
        "Имя: Александр Геворкян\n"
        "Телефон: +7 932 552-01-04\n"
        "Email: stroitexnika1.56@mail.ru\n"
        "\nВы можете позвонить прямо через Telegram:",
        reply_markup=contact_kb
    )
@dp.message(lambda m: m.text == "⬅ Назад")
async def back_from_contacts(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_kb)
# ================== RUN ==================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())