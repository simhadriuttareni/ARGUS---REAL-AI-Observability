from groq import Groq

client = Groq(api_key="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")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=10
)
print(response.choices[0].message.content)