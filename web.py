from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot is running"

@app.route("/run.jsonl")
def run_log():
    if os.path.exists("run.jsonl"):
        return send_file("run.jsonl", mimetype="application/json")
    return "No log file found", 404