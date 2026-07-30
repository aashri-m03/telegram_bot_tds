import os
import json
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

from analyzer import analyze
from logger import save_log


load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN missing")


LOG_FILE = "run.jsonl"


async def handle_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_text = update.message.text

    print("QUESTION:", user_text)


    try:

        answer = analyze(user_text)


        response = {
            "answer": answer,
            "log_url": "https://telegram-bot-tds-9.onrender.com/run.jsonl"
        }


        # save log
        with open(LOG_FILE, "a") as f:
            f.write(
                json.dumps({
                    "time": str(datetime.now()),
                    "question": user_text,
                    "answer": answer
                }) 
                + "\n"
            )


        await update.message.reply_text(
            json.dumps(response)
        )


    except Exception as e:

        error_response = {
            "answer": "ERROR",
            "log_url": "https://telegram-bot-tds-9.onrender.com/run.jsonl"
        }

        await update.message.reply_text(
            json.dumps(error_response)
        )

        print(e)



async def start(update:Update,
                context:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Data Analyst Bot Ready"
    )



def main():

    print("BOT STARTED")


    application = (
        Application
        .builder()
        .token(TOKEN)
        .build()
    )


    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )


    application.add_handler(
        MessageHandler(
            filters.COMMAND,
            start
        )
    )


    application.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )



if __name__ == "__main__":
    main()