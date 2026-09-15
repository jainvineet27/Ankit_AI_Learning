from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI()

user_input = input("Ask your questions (or exit): ")
while True:
    if user_input == "exit":
        print("Have a great day !")
        break
    response = client.responses.create(model="", input=user_input)

    print(response.output_text)
