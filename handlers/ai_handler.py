import requests
import json
from config import GROQ_API_KEY
import re

API_URL = "https://api.groq.com/openai/v1/chat/completions"

dialog_memory = {}
MAX_HISTORY = 6


# ---------- ЗАГРУЗКА ТОВАРОВ ----------
def load_products_text():
    try:
        with open("data/products.json", "r", encoding="utf-8") as f:
            products = json.load(f)

        text = "Товары магазина:\n\n"

        for p in products:
            text += (
                f"Название: {p['name']}\n"
                f"Описание: {p['description']}\n"
                f"Цена: {p.get('price', 'по запросу')}\n\n"
            )

        return text

    except Exception as e:
        print("PRODUCT LOAD ERROR:", e)
        return ""


PRODUCTS_CONTEXT = load_products_text()


SYSTEM_PROMPT = f"""
Ты — AI Robots Assistant.

Ты консультант магазина AI Robots.

Твоя задача:
- помогать выбрать робота
- советовать товары
- объяснять функции
- отвечать кратко и понятно

Используй информацию о товарах ниже:

{PRODUCTS_CONTEXT}

Если пользователь просит совет — рекомендуй конкретный товар.

ВАЖНО:
Если рекомендуешь товар — ОБЯЗАТЕЛЬНО в конце ответа напиши:

[PRODUCT_ID: ID]

пример:
[PRODUCT_ID: 2]
"""


# ---------- AI ----------
def ask_openai(user_id: int, question: str) -> str:

    history = dialog_memory.get(user_id, [])
    history.append({"role": "user", "content": question})
    history = history[-MAX_HISTORY:]
    dialog_memory[user_id] = history

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 400
            },
            timeout=30
        )

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        product_id = None
        match = re.search(r"\[PRODUCT_ID:\s*(\d+)\]", answer)

        if match:
            product_id = int(match.group(1))
            answer = re.sub(r"\[PRODUCT_ID:\s*\d+\]", "", answer).strip()

        dialog_memory[user_id].append({
            "role": "assistant",
            "content": answer
        })

        return answer, product_id

    except Exception as e:
        print("GROQ ERROR:", e)
        return "⚠️ Сейчас ИИ временно недоступен."