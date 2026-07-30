import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


MODEL_URL = "https://router.huggingface.co/v1/chat/completions"



def analyze(question):

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }


    payload = {

        "model": "Qwen/Qwen2.5-7B-Instruct",

        "messages": [

            {
                "role": "system",
                "content": "Answer only final answer. Return JSON: {\"answer\":\"...\"}"
            },

            {
                "role": "user",
                "content": question
            }

        ],

        "max_tokens": 100,
        "temperature": 0

    }


    response = requests.post(
        MODEL_URL,
        headers=headers,
        json=payload,
        timeout=60
    )


    print("HF STATUS:", response.status_code)

    print("HF RESPONSE:", response.text)


    response.raise_for_status()


    data = response.json()


    text = (
        data["choices"][0]
        ["message"]
        ["content"]
    )


    try:

        return json.loads(text)

    except:

        return {
            "answer": text.strip()
        }