from google import genai
from dotenv import load_dotenv
import os 
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client =  genai.Client(api_key=api_key)
user_input = "captial of india"
respone = client.models.generate_content(model = 'gemini-3.5-flash', contents=user_input)

print(respone.text)



