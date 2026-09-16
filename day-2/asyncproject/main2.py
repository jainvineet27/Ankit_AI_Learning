from openai import AsyncOpenAI
from dotenv import load_dotenv
import json 
import asyncio
from orchestrator import concurrent_runs


load_dotenv()
client = AsyncOpenAI()

my_tools = [
    {
        "type": "function",
        "name": "get_stock_details",
        "description": "Provide information on the latest stock details based on user-provided stock code",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_code": {
                    "type": "string",
                    "description": "An NSE stock code provided by user input",
                }
            },
            "required": ["stock_code"],
        },
    }
]

async def main():
    user_input ="can you please provide information on the today stock of reliance , tcs , infy stock_codes"
    response = await  client.responses.create(model="gpt-5.6-luna", input = user_input , tools = my_tools)
    response_id = response.id
    while True:
            functions_calls = [item for item in response.output if item.type=="function_call"]

            if not functions_calls:
                 break 
            
            tools_output= await concurrent_runs(functions_calls)
            response = await client.responses.create(model="gpt-5.6-luna", input = tools_output, previous_response_id=response_id)
            response_id = response.id

    print("\n--- Final Response ---")
    print(response.output_text)


if __name__=="__main__":
    print('this is main class')
    asyncio.run(main())