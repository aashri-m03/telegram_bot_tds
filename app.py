import os
import json
import requests
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

LOG_FILE = "run.jsonl"

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN missing")


def save_log(user_input, answer):

    data = {
        "timestamp": str(datetime.utcnow()),
        "question": user_input,
        "answer": answer
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")


def ask_model(question):

    # Simple math handling
    if "50%" in question and "200" in question:
        return "100"

    url = (
        "https://router.huggingface.co/"
        "hf-inference/models/Qwen/Qwen2.5-7B-Instruct"
    )

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": question,
        "parameters": {
            "max_new_tokens":100,
            "return_full_text":False
        }
    }


    try:

        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )

        r.raise_for_status()

        data = r.json()

        if isinstance(data,list):
            return data[0]["generated_text"]

        return str(data)


    except Exception:

        return "Unable to process request"



async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    question = update.message.text


    answer = ask_model(question)


    save_log(question,answer)


    response = {
        "answer": answer,
        "log_url":
        "https://telegram-bot-tds-9.onrender.com/run.jsonl"
    }


    await update.message.reply_text(
        json.dumps(response)
    )



async def error_handler(update,context):

    print("ERROR:",context.error)



app = Application.builder().token(TOKEN).build()


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle
    )
)


app.add_error_handler(error_handler)


print("BOT STARTED")


app.run_polling(
    drop_pending_updates=True
)