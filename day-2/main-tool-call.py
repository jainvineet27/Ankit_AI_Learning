'''
okay so what odi havr to achivie in this project
 defien dthe user deifned function 
 my tools  whichis oging to act as the tool for thellm 
 thik hai first ftool  
 is getschema iwhich hawe have  and get or detect table name  tools 
 we would be making this two tools and supply to the open ai tool paramters
 
 prompt seciton we have to make ths addition 
 integrate  the app with streamlit 
'''

from dotenv import load_dotenv
import json 
from openai import OpenAI
from connect_to_db import get_schema , get_table
from tools import get_stock_details

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
    "name":"get_schema",
    "type":"function",
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

user_input ="Give me stock related information for TCS  stock code  find out which specific tools needs to be called and then based on that give the output."

response = client.responses.create(model="gpt-5.6-luna", input = user_input , tools = my_tools)

llm_output=response.output 

tool_mapping = {"get_stock_details":get_stock_details}

tools_output=[]

response_id = response.id 

for item in llm_output:
    if  item.type =="function_call":
        f_name  =item.name
        call_id = item.call_id
        args = json.loads(item.arguments)
        f_output = tool_mapping.get(f_name)(**args)
        
        tools_output.append({
            "type":"function_call_output"
            ,"output": f_output
            ,"call_id" : call_id
        })

    response = client.responses.create(model="gpt-5.6-luna", input = tools_output, previous_response_id = response_id)



print("======================================================================")

print(response.output_text)

## it will be having some parts where it mght be making calls to the functions 
tools_output=[]
while True:
    pass
