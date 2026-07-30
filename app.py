import os
import json
import threading
import asyncio

from flask import Flask, send_file
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

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN missing")


LOG_URL = "run.jsonl"


flask_app = Flask(__name__)


telegram_app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)



# -----------------------
# Telegram handlers
# -----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    response = {
        "answer": "Hello! Send me a data analysis question.",
        "log_url": LOG_URL
    }

    await update.message.reply_text(
        json.dumps(response)
    )



async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    question = update.message.text

    print("QUESTION RECEIVED:", question)


    try:

        answer = await asyncio.to_thread(
            analyze,
            question
        )


        print("ANALYZER OUTPUT:", answer)


        save_log(
            question,
            answer
        )


        if isinstance(answer, dict):

            final_answer = answer.get(
                "answer",
                str(answer)
            )

        else:

            final_answer = str(answer)


        response = {
            "answer": final_answer,
            "log_url": LOG_URL
        }


        print("TELEGRAM RESPONSE:", response)


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



# -----------------------
# Flask
# -----------------------

@flask_app.route("/")
def home():

    return "Bot Running"



@flask_app.route("/run.jsonl")
def logs():

    if os.path.exists("run.jsonl"):

        return send_file(
            "run.jsonl",
            mimetype="application/json"
        )

    return "No logs"



def run_flask():

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



# -----------------------
# Start
# -----------------------

if __name__ == "__main__":

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()


    print("Starting Telegram bot...")


    telegram_app.run_polling(
        stop_signals=None
    )