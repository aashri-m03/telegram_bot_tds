import os
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
                "content": "You are a data analyst. Solve the question and return only the answer."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        max_tokens=500
    )

    return {
        "answer": response.choices[0].message.content
    }