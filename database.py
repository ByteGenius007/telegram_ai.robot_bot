import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

db_pool = None

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

async def add_subscriber(user_id: int):
    await db_pool.execute(
        "INSERT INTO subscribers (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
        user_id
    )

async def is_subscriber(user_id: int) -> bool:
    result = await db_pool.fetchrow(
        "SELECT user_id FROM subscribers WHERE user_id=$1",
        user_id
    )
    return result is not None
