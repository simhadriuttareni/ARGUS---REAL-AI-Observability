from groq import Groq
import os

# Read API key from environment variable
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not set in environment")
    exit(1)

client = Groq(api_key=api_key)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=10
)
print(response.choices[0].message.content)