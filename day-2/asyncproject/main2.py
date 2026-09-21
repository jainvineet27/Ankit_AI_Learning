from openai import AsyncOpenAI
from dotenv import load_dotenv
import json 
import asyncio
from orchestrator import concurrent_runs
from my_system_prompt import system_prompt
from connect_to_db_2 import execute_query

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
    },
     {
            "type": "function",
            "name": "get_schema",
            "description": "Provide information available schema which is  reuqired to address the question example sales, courses , departments etc",
            "parameters": {
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "take the schema name which is a logical container of the related tables",
                    },
                    "table_name": {
                                            "type": "string",
                                            "description": "take the table  name which is a store the actual data in the form of rows and columns ",
                                        }
                },
                "required": ["schema_name","table_name"],
            },
        },
         {
                "type": "function",
                "name": "get_table",
                "description": "Provide information on the table which is being fetched based on the identified schema  which contains the table which is matching with user input questions  ",
                "parameters": {
                    "type": "object",
                    "properties": {
                                "schema_name": {
                                    "type": "string",
                                    "description": "take the schema name which is a logical container of the related tables",
                                },
                                "table_name": {
                                                        "type": "string",
                                                        "description": "take the table  name which is a store the actual data in the form of rows and columns ",
                                               }
                                    },
                                    "required": ["schema_name","table_name"],
                },
            }
]

async def main():
    #"can you please provide information on the today stock of reliance , tcs , infy stock_codes"
    user_input="tell me about top 10 departments present under department shema "
    #user_input =
    final_prompt  =f" {system_prompt} and here is the user questions :{user_input}"

    response = await  client.responses.create(model="gpt-5.6-luna", input = final_prompt , tools = my_tools)
    print("first response ...",  response.output[:200])
    response_id = response.id
    max_turns = 5 
    turn=1
    while turn<=max_turns:
            turn+=1
            functions_calls = [item for item in response.output if item.type=="function_call"]
            print("Total funcation calls >>>>>>>>>>>>>>>>>",  len(functions_calls))

            for item in functions_calls:
                print(item.name ,">>>>>>>>>>>>>>>> ",  json.dumps(item.arguments))


            if not functions_calls:
                 break 
            
            tools_output= await concurrent_runs(functions_calls)
            print("tools output >>>>>>>>>>>>>>", tools_output)

            response = await client.responses.create(model="gpt-5.6-luna", input = tools_output, previous_response_id=response_id)
            response_id = response.id

    print("\n--- Final Response ---")
    
    output =execute_query(response.output_text.strip() )
    print("Running the sql query >>>>>>>>> ")
    print(response.output_text)


if __name__=="__main__":
    print('this is main class')
    asyncio.run(main())