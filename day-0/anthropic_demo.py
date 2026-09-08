import os
from anthropic import Anthropic
from dotenv import load_dotenv
from mydb import execute_query, get_schema

# .env file se environment variables load karein
load_dotenv()

# Anthropic client initialize karein
# Yeh default roop se ANTHROPIC_API_KEY environment variable read karta hai
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")  # ya seedhe Anthropic() likhein
)

schema = get_schema('orders')

while True:
    user_input = input("Ask your question: ")
    if user_input.lower() == 'exit':
        break

    # Claude API call
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # ya claude-3-haiku-20240307
        max_tokens=1024,
        system=f"You are a SQL expert. Use this schema to write SQL queries: {schema}",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    # Response extract karne ka syntax
    generated_text = response.content[0].text
    print(generated_text)