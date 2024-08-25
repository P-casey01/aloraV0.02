import openai
import requests

openai.api_key = "OPENAI_API_KEY"

def get_gpt_response(message):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are Alora a state of the art AI that is a personal dietitian your goal is to provide advice that will help the individual achieve their goals "},
                {"role": "user", "content": message},
            ],
            "max_tokens": 2000
        },
        headers={
            'Authorization': f'Bearer {openai.api_key}'
        }
    ).json()

    if response.get('choices') and len(response['choices']) > 0:
        return response['choices'][0]['message']['content']

    return "I'm sorry, I didn't understand that."
