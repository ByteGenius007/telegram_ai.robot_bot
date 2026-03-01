from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🤖 Каталог",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ О компании",
                callback_data="about_company"
            )
        ],
        [
            InlineKeyboardButton(
                text="🌐 Сайт",
                url="https://my-robot-store.great-site.net/"  # ссылка на сайт
            )
        ],
        [
            InlineKeyboardButton(
                text="📞 Контакты",
                callback_data="contacts"
            )
        ]
    ]
)