import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


URL = "https://router.huggingface.co/v1/chat/completions"


SYSTEM_PROMPT = """
You are a data analyst.

Answer the user question.

Return ONLY a valid JSON object.

Rules:
- Do not add markdown.
- Do not add explanations.
- Do not repeat the question.
- Return only required fields.

Examples:

Question:
Which state has highest maternal mortality rate?

Output:
{
 "state": "Assam"
}


Question:
What is 50% of 200?

Output:
{
 "value": 100
}
"""


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
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": question
            }

        ],

        "temperature": 0,

        "max_tokens": 100
    }


    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=60
    )


    print("HF RESPONSE:", response.text)


    response.raise_for_status()


    data = response.json()


    text = (
        data["choices"][0]
        ["message"]
        ["content"]
        .strip()
    )


    # remove markdown if model adds it
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()


    try:
        result = json.loads(text)

        # ensure dictionary
        if isinstance(result, dict):
            return result


    except Exception:
        pass


    # fallback
    return {
        "value": text
    }