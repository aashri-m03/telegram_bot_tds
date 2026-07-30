import json


def save_log(question, answer):

    entry = {
        "question": question,
        "answer": answer
    }


    with open(
        "run.jsonl",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(entry)
            + "\n"
        )