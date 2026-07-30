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
RENDER_URL = os.getenv("RENDER_URL")


if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN missing")


if not RENDER_URL:
    raise ValueError("RENDER_URL missing")


LOG_URL = f"{RENDER_URL}/run.jsonl"


flask_app = Flask(__name__)


telegram_app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    response = {
        "answer": {
            "message": "Hello! Send your data question."
        },
        "log_url": LOG_URL
    }

    await update.message.reply_text(
        json.dumps(response)
    )



async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    question = update.message.text


    try:

        print("QUESTION:", question)


        answer = await asyncio.to_thread(
            analyze,
            question
        )


        print("ANSWER FROM MODEL:", answer)


        save_log(
            question,
            answer
        )


        # Ensure answer is JSON object

        if isinstance(answer, dict):

            final_answer = answer

        else:

            final_answer = {
                "answer": str(answer)
            }



        response = {

            "answer": final_answer,

            "log_url": LOG_URL

        }


        await update.message.reply_text(
            json.dumps(
                response,
                ensure_ascii=False
            )
        )


    except Exception as e:


        response = {

            "answer": {
                "error": str(e)
            },

            "log_url": LOG_URL

        }


        await update.message.reply_text(
            json.dumps(response)
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



@flask_app.route("/")
def home():

    return "Bot running"



@flask_app.route("/run.jsonl")
def logs():

    if os.path.exists("run.jsonl"):

        return send_file(
            "run.jsonl",
            mimetype="application/json"
        )

    return "No logs found",404




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



if __name__ == "__main__":


    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()


    telegram_app.run_polling(
        stop_signals=None
    )