import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


MODEL_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"


def analyze(question):

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {
        "inputs": question,
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0
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

        answer = data[0]["generated_text"]

    else:

        return {
            "answer": str(data)
        }


    return {
        "answer": answer.strip()
    }