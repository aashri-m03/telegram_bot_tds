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
    raise ValueError("TELEGRAM_TOKEN missing")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a data analysis question."
    )


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("MESSAGE RECEIVED:", update.message.text)

    user_text = update.message.text

    try:
        answer = analyze(user_text)

        # Save logs separately
        save_log(
            user_text,
            answer
        )

        # Ensure only JSON object is sent to grader
        if isinstance(answer, dict):
            final_response = answer
        else:
            final_response = {
                "answer": answer
            }

        await update.message.reply_text(
            json.dumps(final_response)
        )

    except Exception as e:

        print("ERROR:", e)

        # Return JSON only
        await update.message.reply_text(
            json.dumps({
                "error": str(e)
            })
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


app.add_handler(
    CommandHandler("start", start)
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)


print("Bot started...")

app.run_polling()