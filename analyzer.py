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

Return only JSON.

Format:

{
 "answer": "your answer"
}

Do not mention logs.
Do not mention files.
Do not mention log_url.
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

        text = data[0]["generated_text"]

    else:

        text = str(data)


    try:

        return json.loads(text)

    except:

        return {
            "answer": text
        }