import os
import json
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    api_key=HF_TOKEN
)

SYSTEM_PROMPT = """
You are an expert data analyst.

Rules:
1. Answer the user's question.
2. Return ONLY valid JSON.
3. Never use markdown.
4. Never explain.
5. If the user specifies a JSON format, follow it exactly.
6. Otherwise return:
{
  "answer": ...
}
"""


def analyze(question):

    response = client.chat_completion(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ],
        max_tokens=800,
        temperature=0
    )

    text = response.choices[0].message.content.strip()

    try:
        return json.loads(text)

    except Exception:

        return {
            "answer": text
        }