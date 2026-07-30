import os
import json

from huggingface_hub import InferenceClient


HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing")


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

    try:

        # Create fresh client every request
        client = InferenceClient(
            api_key=HF_TOKEN
        )


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


        # Remove markdown if returned
        if text.startswith("```"):

            text = (
                text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )


        result = json.loads(text)


        return {
            "answer": result.get(
                "answer",
                text
            )
        }


    except Exception as e:

        print("Analyzer error:", e)

        return {
            "answer": f"Unable to analyze: {str(e)}"
        }