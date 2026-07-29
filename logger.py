import json
from datetime import datetime

LOG_FILE = "run.jsonl"


def save_log(question, answer):

    data = {
        "timestamp": str(datetime.now()),
        "question": question,
        "answer": answer
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")