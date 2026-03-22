from groq import Groq
import time
from app.config import get_settings

settings = get_settings()

client = Groq(api_key=settings.GROQ_API_KEY)

MODEL = "llama-3.1-8b-instant"   


def generate_response(prompt: str):
    start = time.time()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI. Explain clearly and accurately without repetition."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=300
    )

    text = response.choices[0].message.content

    latency = (time.time() - start) * 1000

    return text, latency