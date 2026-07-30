import os
import json
import asyncio
import threading

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


LOG_URL = os.getenv(
    "LOG_URL",
    "run.jsonl"
)


app = Flask(__name__)


telegram_app = (
    Application
    .builder()
    .token(TOKEN)
    .build()
)



async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    response = {
        "answer": "Hello! Send me a data analysis question.",
        "log_url": LOG_URL
    }


    await update.message.reply_text(
        json.dumps(response)
    )



async def reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    question = update.message.text


    try:

        answer = await asyncio.to_thread(
            analyze,
            question
        )


        save_log(
            question,
            answer
        )


        response = {

            "answer": answer.get(
                "answer",
                str(answer)
            ),

            "log_url": LOG_URL
        }


        await update.message.reply_text(
            json.dumps(
                response,
                ensure_ascii=False
            )
        )


    except Exception as e:

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



@app.route("/")
def home():

    return "Bot running"



@app.route("/run.jsonl")
def logs():

    if os.path.exists("run.jsonl"):

        return send_file(
            "run.jsonl",
            mimetype="application/json"
        )


    return "No logs yet"



def run_bot():

    asyncio.run(
        telegram_app.run_polling()
    )



if __name__ == "__main__":


    bot_thread = threading.Thread(
        target=run_bot,
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