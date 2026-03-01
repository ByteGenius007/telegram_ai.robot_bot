import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, KeyboardButton, ReplyKeyboardMarkup, InputMediaPhoto
from aiogram import F

from config import BOTS
from keyboards.menu_kb import main_menu_kb
from keyboards.products_kb import get_products_keyboard
from handlers.ai_handler import ask_openai
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message

from database import is_subscriber
from database import add_subscriber

bot = Bot(token=BOTS["airobots"])
dp = Dispatcher()
ai_mode_users = set()
# Кнопка запроса номера телефона для проверки, что человек
phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Я не робот (отправить номер телефона)", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
ai_exit_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Выйти из AI-консультанта",
                callback_data="exit_ai"
            )
        ]
    ]
)
# Функция отправки основного приветствия и меню
async def send_start_message(message: types.Message):
    photo = FSInputFile("media/photos/welcome.jpg")
    user_name = message.from_user.first_name or "друг"

    await message.answer_photo(
        photo=photo,
        caption=(
            f"Привет, {user_name}! 👋\n\n"
            "Добро пожаловать в AI Robots 🤖\n\n"
            "Мы помогаем подобрать роботов для:\n"
            "• бизнеса\n"
            "• мероприятий\n"
            "• аренды и покупки\n\n"
            "Выбери нужный раздел ниже 👇"
        )
    )

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_kb
    )

# Старт бота
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id

    if not await is_subscriber(user_id):
        await message.answer(
            "Привет! Перед тем как начать, подтвердите, что вы человек 👇",
            reply_markup=phone_kb
        )
        return

    await send_start_message(message)


# Обработка контакта (проверка "не робот")

@dp.message(F.contact)
async def phone_confirm(message: types.Message):
    user_id = message.from_user.id

    await add_subscriber(user_id)
    await send_start_message(message)


@dp.callback_query(F.data == "about_company")
async def about_company(callback: types.CallbackQuery):
    await callback.answer()

    video = FSInputFile("media/videos/robot1.mp4")

    await callback.message.answer(
        "🤖 AI Robots — магазин и аренда современных роботов.\n\n"
        "Мы предлагаем:\n"
        "• роботов для бизнеса\n"
        "• промо-роботов\n"
        "• аренду на мероприятия\n"
        "• консультацию и поддержку\n\n"
        "Сайт: https://my-robot-store.great-site.net/"
    )

    await callback.message.answer_video(
        video=video,
        caption="Посмотри, как работают наши роботы 🚀"
    )

    await callback.message.answer(
        "Выбери раздел 👇",
        reply_markup=main_menu_kb
    )


    


@dp.callback_query(F.data == "products")
async def products(callback: types.CallbackQuery):
    
    with open("data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    keyboard = get_products_keyboard(products)
    # Редактируем текст (текстное сообщение -> список кнопок)
    await callback.message.edit_text(
        "Выбери 👇",
        reply_markup=keyboard
    )
    await callback.answer()



@dp.callback_query(F.data.startswith("product:"))
async def open_product(callback: types.CallbackQuery):
    product_id = callback.data.split(":")[1]

    with open("data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    product = next(p for p in products if p["id"] == product_id)

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(product["photo"]),
            caption=f"<b>{product['name']}</b>\n\n{product['description']}",
            parse_mode="HTML"
        ),
        reply_markup=get_products_keyboard(products)
    )

    await callback.answer()




@dp.callback_query(F.data == "back_to_products_menu")
async def back_to_products(callback: types.CallbackQuery):

    
    await callback.message.delete()

    # меню
    await callback.message.answer(
        "Выбери, что хочешь узнать дальше 👇",
        reply_markup=main_menu_kb
    )
    await callback.answer()

@dp.callback_query(F.data == "contacts")
async def show_contacts(callback: types.CallbackQuery):
    await callback.answer()  # убираем "час ожидания"
    
    contact_text = (
        "🏢 Адрес:\n"
        "г. Астана, Казахстан\n\n"
        "📞 Телефон:\n"
        "+7 (700) 000-00-00\n\n"
        "✉ Email:\n"
        "info@ai-robots.kz"
    )

    await callback.message.answer(contact_text)
    await callback.message.answer(
        "Выбери, что хочешь узнать дальше 👇",
        reply_markup=main_menu_kb
    )
@dp.callback_query(F.data == "ai_assistant")
async def ai_assistant(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    ai_mode_users.add(user_id)

    await callback.message.answer(
        "🤖 <b>AI-консультант активирован</b>\n\n"
        "Теперь ты можешь просто написать вопрос.\n\n"
        "Например:\n"
        "• Какой робот подойдёт для бизнеса?\n"
        "• Сколько стоит аренда?\n"
        "• Посоветуй робота для мероприятия\n\n"
        "Просто напиши сообщение 👇",
        parse_mode="HTML",
        reply_markup=ai_exit_kb
    )
@dp.callback_query(F.data == "exit_ai")
async def exit_ai(callback: types.CallbackQuery):
    await callback.answer()

    user_id = callback.from_user.id
    ai_mode_users.discard(user_id)

    await callback.message.answer(
        "✅ Ты вышел из AI-консультанта.\n\n"
        "Выбери раздел меню 👇",
        reply_markup=main_menu_kb
    )

@dp.message()
async def messages_router(message: types.Message):
    text = message.text
    if not text:
        return

    # --- КНОПКИ ГЛАВНОГО МЕНЮ (ИИ НЕ РАБОТАЕТ) ---
    menu_buttons = [
        "lol"
    ]

    if text in menu_buttons or text.startswith("/"):
        return

    # --- ПРОВЕРКА ТОВАРОВ (ИИ НЕ ЛЕЗЕТ) ---
    try:
        with open("data/products.json", "r", encoding="utf-8") as f:
            products = json.load(f)

        for product in products:
            if text == product["button"]:
                photo = FSInputFile(product["photo"])
                await message.answer_photo(
                    photo=photo,
                    caption=f"{product['name']}\n\n{product['description']}",
                    reply_markup=main_menu_kb  # меню ВСЕГДА видно
                )
                return
    except Exception as e:
        print("Ошибка при проверке товаров:", e)

    # --- ЕСЛИ НЕ В РЕЖИМЕ AI → игнор ---
    if message.from_user.id not in ai_mode_users:
        return

    # --- AI ОТВЕТ ---
    try:
        msg = await message.answer("🤖 Думаю...")

        answer, product_id = ask_openai(message.from_user.id, text)

        if product_id:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🤖 Открыть товар",
                            url=f"https://my-robot-store.great-site.net/product?id={product_id}"
                        )
                    ]
                ]
            )

            await message.answer(answer, reply_markup=keyboard)
            await message.answer("Хочешь выйти из AI-консультанта? Выбери 👇", reply_markup=ai_exit_kb)
        else:
            await message.answer(answer, reply_markup=ai_exit_kb)

        await msg.delete()

    except Exception as e:
        print("AI ERROR:", e)
        await message.answer("⚠️ Сейчас не могу ответить, попробуй позже 🙏", reply_markup=main_menu_kb)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    print("AI Robots bot started")
