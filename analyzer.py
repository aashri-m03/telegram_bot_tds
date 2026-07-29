import os
import json
from huggingface_hub import InferenceClient


HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    api_key=HF_TOKEN
)


def analyze(question):

    response = client.chat_completion(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a data analyst. "
                    "Answer the user's question. "
                    "Return ONLY a valid JSON object. "
                    "No markdown, no explanation."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        max_tokens=500
    )

    text = response.choices[0].message.content.strip()

    try:
        # Convert AI JSON text into Python dictionary
        return json.loads(text)

    except json.JSONDecodeError:
        # fallback if model returns plain text
        return {
            "answer": text
        }