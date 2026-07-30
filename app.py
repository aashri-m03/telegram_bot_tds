import os
import json

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

WEBHOOK_PATH = "telegram-webhook"


app = Flask(__name__)


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


        save_log(
            user_text,
            answer
        )


        if isinstance(answer, dict):

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

        print("ERROR:", str(e))


        await update.message.reply_text(
            json.dumps(
                {
                    "error": str(e),
                    "log_url": LOG_URL
                }
            )
        )



telegram_app.add_handler(
    CommandHandler(
        "start",
        start
    )
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

@app.route("/")
def home():

    return "Telegram Bot Running"



@app.route("/run.jsonl")
def logs():

    if os.path.exists("run.jsonl"):

        return send_file(
            "run.jsonl",
            mimetype="application/json"
        )

    return "No logs found", 404



# Telegram webhook

@app.post(f"/{WEBHOOK_PATH}")
async def webhook():

    data = request.get_json(force=True)


    update = Update.de_json(
        data,
        telegram_app.bot
    )


    await telegram_app.process_update(
        update
    )


    return "OK"



# -----------------------------
# Initialize webhook
# -----------------------------

async def setup_bot():

    await telegram_app.initialize()

    await telegram_app.start()


    webhook_url = (
        f"{RENDER_URL}/{WEBHOOK_PATH}"
    )


    await telegram_app.bot.set_webhook(
        webhook_url
    )


    print(
        "Webhook set:",
        webhook_url
    )



# -----------------------------
# Run server
# -----------------------------

if __name__ == "__main__":

    import asyncio

    asyncio.run(
        setup_bot()
    )


    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )