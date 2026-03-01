import os
from dotenv import load_dotenv

load_dotenv()

BOTS = {
    "airobots": os.getenv("BOT_MARAT"),
}

ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # важно привести к int

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
