import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing")


MODEL_URL = (
    "https://router.huggingface.co/"
    "hf-inference/models/Qwen/Qwen2.5-7B-Instruct"
)


SYSTEM_PROMPT = """
You are a data analyst.

Rules:
- Return only the final answer.
- Do not repeat the question.
- Do not explain.
- Return valid JSON only.

Format:

{
 "answer": "final answer"
}
"""


def analyze(question):

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {
        "inputs": (
            SYSTEM_PROMPT
            + "\nQuestion: "
            + question
        ),
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0,
            "return_full_text": False
        }
    }


    response = requests.post(
        MODEL_URL,
        headers=headers,
        json=payload,
        timeout=60
    )


    response.raise_for_status()


    data = response.json()


    if isinstance(data, list):

        text = data[0]["generated_text"]

    else:

        return {
            "answer": str(data)
        }


    try:

        result = json.loads(text)

        return {
            "answer": result["answer"]
        }

    except:

        return {
            "answer": text.strip()
        }