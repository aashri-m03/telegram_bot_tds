import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


MODEL_URL = "https://router.huggingface.co/v1/chat/completions"



SYSTEM_PROMPT = """

You are a data analyst.

Answer the user's question.

Return ONLY valid JSON.

Do not repeat the question.

Do not add explanations.

Examples:

User:
Which state has the highest maternal mortality rate?

Output:

{
 "state": "Assam"
}

User:
What is 50% of 200?

Output:

{
 "value": 100
}

"""



def analyze(question):


    headers = {

        "Authorization":
        f"Bearer {HF_TOKEN}",

        "Content-Type":
        "application/json"

    }



    payload = {


        "model":
        "Qwen/Qwen2.5-7B-Instruct",


        "messages":

        [

            {
                "role":"system",
                "content":SYSTEM_PROMPT
            },

            {
                "role":"user",
                "content":question
            }

        ],


        "temperature":0,


        "max_tokens":200

    }



    response = requests.post(

        MODEL_URL,

        headers=headers,

        json=payload,

        timeout=60

    )


    response.raise_for_status()



    data = response.json()



    text = (

        data["choices"][0]

        ["message"]

        ["content"]

        .strip()

    )



    try:

        return json.loads(text)


    except:


        return {

            "answer": text

        }