import os
import json

from huggingface_hub import InferenceClient


HF_TOKEN = os.getenv("HF_TOKEN")


if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing")


SYSTEM_PROMPT = """
You are an expert data analyst.

Rules:
1. Give only the final answer.
2. Do not repeat the user's question.
3. Do not explain unless the user asks for explanation.
4. Return ONLY valid JSON.
5. Never use markdown.
6. Never mention logs.
7. Never mention files.
8. Never mention log_url.

Return exactly:

{
 "answer": "final answer only"
}


Examples:

Question:
What is 50% of 200?

Answer:
{
 "answer": "100"
}


Question:
Which state has the highest maternal mortality rate?

Answer:
{
 "answer": "Kerala"
}
"""


def analyze(question):

    try:

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

            max_tokens=200,

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

        print("Analyzer error:", e)

        return {
            "answer": str(e)
        }