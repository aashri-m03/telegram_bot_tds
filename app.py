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
RENDER_URL = os.getenv("RENDER_URL")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN missing")

if not RENDER_URL:
    raise ValueError("RENDER_URL missing")

LOG_URL = f"{RENDER_URL}/run.jsonl"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a data analysis question."
    )


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text
    print("MESSAGE RECEIVED:", user_text)

    try:
        answer = analyze(user_text)

        # Save the interaction
        save_log(user_text, answer)

        # If analyzer already returns {"answer": ...}
        if isinstance(answer, dict) and "answer" in answer:
            response = answer
        else:
            response = {
                "answer": answer
            }

        # Add log URL
        response["log_url"] = LOG_URL

        await update.message.reply_text(
            json.dumps(response, ensure_ascii=False)
        )

    except Exception as e:

        print("ERROR:", e)

        await update.message.reply_text(
            json.dumps(
                {
                    "error": str(e),
                    "log_url": LOG_URL
                },
                ensure_ascii=False
            )
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

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)

print("Bot started...")

app.run_polling()