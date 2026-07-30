import json
import os
from datetime import datetime

LOG_FILE = "run.jsonl"

def save_log(question, answer):

    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")