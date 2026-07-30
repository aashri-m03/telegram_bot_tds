import os
import json
import asyncio

from flask import Flask, request, send_file
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

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


# Flask app for Render
flask_app = Flask(__name__)


# Telegram application
telegram_app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)


# -----------------------------
# Telegram handlers
# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Hello! Send me a data analysis question."
    )


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    print("Received:", user_text)

    try:

        answer = analyze(user_text)

        print("Answer:", answer)

        save_log(user_text, answer)


        if isinstance(answer, dict) and "answer" in answer:
            response = answer
        else:
            response = {
                "answer": answer
            }


        response["log_url"] = LOG_URL


        await update.message.reply_text(
            json.dumps(
                response,
                ensure_ascii=False
            )
        )


    except Exception as e:

        print("ERROR:", e)

        await update.message.reply_text(
            json.dumps(
                {
                    "error": str(e),
                    "log_url": LOG_URL
                }
            )
        )


telegram_app.add_handler(
    CommandHandler("start", start)
)


telegram_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        reply
    )
)


# -----------------------------
# Flask routes
# -----------------------------

@flask_app.route("/")
def home():

    return "Telegram Bot Running"


@flask_app.route("/run.jsonl")
def logs():

    if os.path.exists("run.jsonl"):

        return send_file(
            "run.jsonl",
            mimetype="application/json"
        )

    return "No logs found", 404



# Telegram webhook endpoint

@flask_app.post(f"/{TOKEN}")
def webhook():

    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )


    asyncio.run(
        telegram_app.process_update(update)
    )


    return "OK"



# -----------------------------
# Start Telegram webhook
# -----------------------------

def setup_bot():

    async def init():

        await telegram_app.initialize()

        await telegram_app.start()

        await telegram_app.bot.set_webhook(
            f"{RENDER_URL}/{TOKEN}"
        )

        print(
            "Webhook set:",
            f"{RENDER_URL}/{TOKEN}"
        )


    asyncio.run(init())



# -----------------------------
# Run Render server
# -----------------------------

if __name__ == "__main__":

    setup_bot()

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    flask_app.run(
        host="0.0.0.0",
        port=port
    )