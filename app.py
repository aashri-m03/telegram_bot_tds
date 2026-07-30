import os
import json
import threading
import asyncio

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

    try:

        # Get answer from LLM
        result = analyze(question)


        # Save JSONL log
        save_log(
            question,
            result
        )


        # Required assignment format
        response = {
            "answer": result,
            "log_url": RENDER_URL.rstrip("/") + "/run.jsonl"
        }


        await update.message.reply_text(
            json.dumps(response)
        )


    except Exception as e:

        print("ERROR:", e)

        response = {
            "answer": {
                "error": str(e)
            },
            "log_url": RENDER_URL.rstrip("/") + "/run.jsonl"
        }

        await update.message.reply_text(
            json.dumps(response)
        )



def start_bot():

    # Fix Python 3.14 event loop issue
    asyncio.set_event_loop(
        asyncio.new_event_loop()
    )


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


    print("BOT STARTED")


    application.run_polling(
        drop_pending_updates=True
    )



if __name__ == "__main__":


    threading.Thread(
        target=start_bot,
        daemon=True
    ).start()


    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )