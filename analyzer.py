import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


MODEL_URL = (
    "https://api-inference.huggingface.co/"
    "models/Qwen/Qwen2.5-7B-Instruct"
)


SYSTEM_PROMPT = """
You are an expert data analyst.

Rules:
- Return ONLY valid JSON.
- Do not use markdown.
- Do not mention logs.
- Do not mention files.
- Do not mention log_url.

Return exactly:

{
 "answer": "your answer"
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
            + "\nUser question: "
            + question
        ),

        "parameters": {
            "max_new_tokens": 800,
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


    data = response.json()


    if isinstance(data, list):

        text = data[0]["generated_text"]

    else:

        return {
            "answer": str(data)
        }


    # Remove markdown if model adds it
    text = (
        text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


    try:

        result = json.loads(text)

        return {
            "answer": result.get(
                "answer",
                text
            )
        }


    except Exception:

        return {
            "answer": text
        }