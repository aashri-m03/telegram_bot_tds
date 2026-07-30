import os
import json

from huggingface_hub import InferenceClient


HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing")


client = InferenceClient(
    api_key=HF_TOKEN
)


SYSTEM_PROMPT = """
You are an expert data analyst.

Rules:
1. Answer the user's question.
2. Output ONLY valid JSON.
3. Do not use markdown.
4. Do not add explanations outside JSON.
5. If the user gives a JSON format, follow it exactly.
6. Otherwise output:

{
  "answer": "your answer here"
}
"""


def analyze(question):

    try:

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


        text = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )


        # Remove accidental markdown fences
        if text.startswith("```"):
            text = (
                text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )


        return json.loads(text)


    except json.JSONDecodeError:

        return {
            "answer": text
        }


    except Exception as e:

        return {
            "error": str(e)
        }