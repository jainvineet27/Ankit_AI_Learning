from dotenv import load_dotenv
import json 
from connect_to_db import get_schema , get_table
from tools import get_stock_details

from openai import OpenAI 
from my_system_prompt import system_prompt

load_dotenv()

my_tools  =[
{
    "type": "function",
    "name":"get_stock_details",
    "description" :"it return the details associated with the provided stock code",
    "parameters" :    {
        "type":"object",
        "properties": { 
            "stock_code" :
                        {
                            "type":"string" , 
                            "description" : "a NSE  unique code which tell stock information for a particular stock price"
                        }
        },
        "required" :["stock_code"]

    }
}

,{
    "type":"function",
    "name":"get_schema",    
    "description":"get the name of the schema of the table",
    "parameters" :{
            "type":"object",
            "properties" : {
                "table_name":{
                    "type":"string",
                    "description":"represente name of the table in question"
                }
            },
            "required":["table_name"]
                }  
}
]

client = OpenAI()

#"Give me stock related information for TCS  stock code  find out which specific tools needs to be called and then based on that give the output."
user_input ="Give me the top 10 sales for the customers"
prompt =f''' 
{system_prompt} 
Here is the user Question :
{user_input}
'''


response = client.responses.create(model="gpt-5.6-luna", input = user_input , tools = my_tools )

llm_output=response.output 
tool_mapping = {"get_stock_details":get_stock_details, "get_schema":get_schema}

response_id = response.id 
print("======================================================================")


## it will be having some parts where it mght be making calls to the functions 
while True:
    tools_output=[]    
    for item in llm_output:        
        if  item.type =="function_call":
            f_name  =item.name
            call_id = item.call_id
            args = json.loads(item.arguments)
            f_output = json.dumps(tool_mapping.get(f_name)(**args))
            print("f_output >>>>>>>>>>>>>>>>>>" , f_output)
            
            tools_output.append({
                "type":"function_call_output"
                ,"output": f_output
                ,"call_id" : call_id
            })

            print(json.dumps(tools_output,indent=4))
           

    if not tools_output:
        break
    
    response = client.responses.create(model="gpt-5.6-luna", input = tools_output, previous_response_id = response_id)    
    response_id = response.id
    llm_output= response.output

print(response.output_text)


