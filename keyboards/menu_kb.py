from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📖 Подробнее о компании",
                callback_data="about_company"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Узнать о продукции",
                callback_data="products"
            )
        ]
    ]
)
