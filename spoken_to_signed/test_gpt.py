from openai import OpenAI
from config import *

client = OpenAI(
    api_key=apikey,
)

def test_text(user_input_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input_text}]
    )


    result = response.choices[0].message.content
    return result

if __name__ == "__main__":
    input_text = "Hello, everyone tries to rig it. Don’t you? What is the ASL representation of this sentence?"
    result = test_text(input_text)
    print(result)

