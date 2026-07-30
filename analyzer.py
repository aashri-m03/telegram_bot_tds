import os
import json
import requests


HF_TOKEN = os.getenv("HF_TOKEN")


URL = "https://router.huggingface.co/v1/chat/completions"



SYSTEM_PROMPT = """

You are a data analyst.

Answer the user question.

Return ONLY JSON.

Never repeat the question.

Never add explanations.

Examples:

Question:
Which state has highest maternal mortality rate?

Output:
{
 "state":"Assam"
}


Question:
What is 50% of 200?

Output:
{
 "value":100
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

        "max_tokens":100

    }



    r = requests.post(

        URL,

        headers=headers,

        json=payload,

        timeout=60

    )


    print(
        "HF RESPONSE:",
        r.text
    )


    r.raise_for_status()


    data = r.json()



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