import os
import json
import asyncio
import threading

from flask import Flask, send_file

from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

from analyzer import analyze
from logger import save_log


TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")


app = Flask(__name__)


@app.route("/")
def home():
    return "BOT RUNNING"


@app.route("/run.jsonl")
def logs():
    return send_file(
        "run.jsonl",
        mimetype="application/jsonl"
    )


async def handle_message(update, context):

    question = update.message.text

    result = analyze(question)

    save_log(
        question,
        result
    )

    response = {
        "answer": result,
        "log_url": RENDER_URL.rstrip("/") + "/run.jsonl"
    }

    await update.message.reply_text(
        json.dumps(response)
    )



def create_bot():

    application = (
        Application
        .builder()
        .token(TOKEN.strip())
        .build()
    )


    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    return application



def start_bot():

    asyncio.run(bot_main())



async def bot_main():

    application = create_bot()

    await application.initialize()

    await application.start()

    await application.updater.start_polling(
        drop_pending_updates=True
    )

    print("BOT STARTED")

    await asyncio.Event().wait()



if __name__ == "__main__":

    # Start Telegram bot in background
    threading.Thread(
        target=start_bot,
        daemon=True
    ).start()


    # Start Flask for Render
    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )