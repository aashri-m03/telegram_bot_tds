import os
import json
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

from telegram.request import HTTPXRequest

from analyzer import analyze
from logger import save_log


load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN missing in .env")


LOG_URL = "https://raw.githubusercontent.com/aashri-m03/telegram_bot_tds/refs/heads/main/run.jsonl"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a data analysis question."
    )


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("MESSAGE RECEIVED:", update.message.text)

    user_text = update.message.text

    try:

        answer = analyze(user_text)

        save_log(
            user_text,
            answer
        )

        # Remove nested answer if analyzer returns {"answer": value}
        if isinstance(answer, dict) and "answer" in answer:
            final_answer = answer["answer"]
        else:
            final_answer = answer

        response = {
            "answer": final_answer,
            "log_url": LOG_URL
        }

        await update.message.reply_text(
            json.dumps(response)
        )


    except Exception as e:

        print("ERROR:", e)

        error_response = {
            "answer": str(e),
            "log_url": LOG_URL
        }

        await update.message.reply_text(
            json.dumps(error_response)
        )


request = HTTPXRequest(
    connect_timeout=60,
    read_timeout=60,
    write_timeout=60,
    pool_timeout=60
)


app = (
    ApplicationBuilder()
    .token(TOKEN)
    .request(request)
    .build()
)


# /start command
app.add_handler(
    CommandHandler("start", start)
)


# Text questions
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)


print("Bot started...")

app.run_polling()