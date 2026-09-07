from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(
    base_url=os.getenv(
        "FREELLMAPI_BASE_URL",
        "http://127.0.0.1:31415/v1",
    ),
    api_key=os.getenv("FREELLMAPI_API_KEY"),
)


response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {
            "role": "user",
            "content": "Explain what this Python function does:\n\n"
            "def add(a, b):\n"
            "    return a + b",
        }
    ],
)

print(response.choices[0].message.content)