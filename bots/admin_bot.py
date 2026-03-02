import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InputMediaPhoto

from config import ADMIN_BOT_TOKEN, ADMIN_ID, BOTS

import database
from database import init_db

bot = Bot(token=ADMIN_BOT_TOKEN)
dp = Dispatcher()


# ---------------- Загрузка медиа ----------------
async def download_media(admin_bot: Bot, file_id: str, dest_path: str):
    file = await admin_bot.get_file(file_id)
    await admin_bot.download_file(file.file_path, destination=dest_path)


# ---------------- Получение подписчиков из БД ----------------
async def get_subscribers():
    rows = await database.db_pool.fetch(
        "SELECT user_id FROM subscribers"
    )
    return [r["user_id"] for r in rows]


# ---------------- Команда рассылки ----------------
@dp.message(Command("news"))
async def send_news(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа ❌")
        return

    text = message.text.replace("/news", "").strip() if message.text else None

    photo_paths = []
    video_path = None

    try:
        # -------- фото --------
        if message.photo:
            for i, photo in enumerate(message.photo):
                fid = photo.file_id
                path = f"temp_news_photo_{i}_{fid}.jpg"
                await download_media(bot, fid, path)
                photo_paths.append(path)

        # -------- видео --------
        if message.video:
            fid = message.video.file_id
            video_path = f"temp_news_video_{fid}.mp4"
            await download_media(bot, fid, video_path)

        if not text and not photo_paths and not video_path:
            await message.answer("Напиши текст или прикрепи фото/видео")
            return

        # ✅ берём пользователей из PostgreSQL
        subscribers = await get_subscribers()

        # -------- рассылка --------
        for bot_name, token in BOTS.items():
            async with Bot(token=token) as bot_instance:

                for user_id in subscribers:
                    try:
                        # несколько фото
                        if len(photo_paths) > 1:
                            media_group = [
                                InputMediaPhoto(
                                    media=FSInputFile(p),
                                    caption=text if i == 0 and text else None
                                )
                                for i, p in enumerate(photo_paths)
                            ]
                            await bot_instance.send_media_group(
                                user_id,
                                media=media_group
                            )

                        # одно фото
                        elif len(photo_paths) == 1:
                            await bot_instance.send_photo(
                                user_id,
                                photo=FSInputFile(photo_paths[0]),
                                caption=text if text else None
                            )

                        # видео
                        elif video_path:
                            await bot_instance.send_video(
                                user_id,
                                video=FSInputFile(video_path),
                                caption=text if text else None
                            )

                        # только текст
                        else:
                            await bot_instance.send_message(
                                user_id,
                                text=f"📢 Новость:\n\n{text}"
                            )

                    except Exception as e:
                        print(f"Не удалось отправить {user_id}: {e}")

        await message.answer("Новость разослана ✅")

    finally:
        # -------- очистка файлов --------
        for p in photo_paths:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except:
                pass


# ---------------- Запуск ----------------
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())