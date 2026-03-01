import asyncio
from bots.airobots_bot import dp as dp_airobots, bot as bot_airobots
from bots.admin_bot import dp as dp_admin, bot as bot_admin
import os
import sys
from database import init_db
async def main():
    if os.getenv("BOT_ENABLED") == "false":
        print("Bot disabled")
        sys.exit()
    
    await init_db()
    # запускаем оба бота параллельно
    await asyncio.gather(
        dp_airobots.start_polling(bot_airobots),
        dp_admin.start_polling(bot_admin)
    )

if __name__ == "__main__":
    asyncio.run(main())
