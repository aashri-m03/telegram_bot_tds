import os
import json

from huggingface_hub import InferenceClient


HF_TOKEN = os.getenv("HF_TOKEN")


if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing")



SYSTEM_PROMPT = """
You are a data analyst.

Answer the user's question.

Rules:
- Return ONLY JSON.
- Do not use markdown.
- Do not mention logs.
- Do not mention files.
- Do not mention log_url.
- Do not add explanations.

Always return exactly:

{
  "answer": "your answer"
}
"""



def analyze(question):

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


    # Remove markdown blocks
    if text.startswith("```"):

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