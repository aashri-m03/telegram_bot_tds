import os
import json
import asyncio
import threading

from flask import Flask, send_file
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
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
    raise ValueError("TELEGRAM_TOKEN is missing")

if not RENDER_URL:
    raise ValueError("RENDER_URL is missing")


app = Flask(__name__)


# -------------------------
# Flask endpoints
# -------------------------

@app.route("/")
def home():
    return "Telegram bot running"


@app.route("/run.jsonl")
def run_log():
    return send_file(
        "run.jsonl",
        mimetype="application/jsonl"
    )


# -------------------------
# Telegram handler
# -------------------------

async def handle_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    question = update.message.text


    try:

        # analyzer should return:
        # {"state": "Assam"}

        answer = analyze(question)


    except Exception as e:

        answer = {
            "error": str(e)
        }


    # save JSONL log
    log_entry = {
        "question": question,
        "answer": answer
    }

    save_log(log_entry)



    # EXACT REQUIRED FORMAT
    response = {
        "answer": answer,
        "log_url": f"{RENDER_URL}/run.jsonl"
    }


    # ONLY JSON OBJECT
    await update.message.reply_text(
        json.dumps(response)
    )



# -------------------------
# Telegram polling
# -------------------------

def start_bot():

    # Python 3.14 fix
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )


    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )


    print("BOT STARTED")


    application.run_polling(
        drop_pending_updates=True,
        close_loop=False,
        stop_signals=None
    )



# -------------------------
# Main
# -------------------------

if __name__ == "__main__":


    bot_thread = threading.Thread(
        target=start_bot,
        daemon=True
    )

    bot_thread.start()


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