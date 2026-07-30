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
You are an expert data analyst.

Rules:
1. Answer the user's question.
2. Return ONLY valid JSON.
3. Never use markdown.
4. Never mention logs.
5. Never mention files.
6. Never mention log_url.

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
            + "\n\nUser question:\n"
            + question
        ),

        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0,
            "return_full_text": False
        }
    }


    try:

        response = requests.post(
            MODEL_URL,
            headers=headers,
            json=payload,
            timeout=60
        )


        response.raise_for_status()


        data = response.json()


        if isinstance(data, list):

            text = data[0].get(
                "generated_text",
                ""
            )

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


    except Exception as e:

        print("HuggingFace Error:", e)

        return {
            "answer": f"Unable to process request: {str(e)}"
        }