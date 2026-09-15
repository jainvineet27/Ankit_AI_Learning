'''
okay so what odi havr to achivie in this project
 defien dthe user deifned function 
 my tools  whichis oging to act as the tool for thellm 
 thik hai first ftool  
 is getschema iwhich hawe have  and get or detect table name  tools 
 we would be making this two tools and supply to the open ai tool paramters
 
 prompt seciton we have to make ths addition 
 
 itnegrate the app with streamlit 
'''

from dotenv import load_dotenv
import json 
from openai import OpenAI
from connect_to_db import get_schema

load_dotenv()


def get_stock_info(stock_code:str) -> str: 
    d = {"TCS" : 1990, "INFY":200}

    return str(d.get(stock_code,""))

my_tools  =[
{
    "type": "function",
    "name":"get_stock_info",
    "description" :"it return the details associated with the provided stock code",
    "parameters" :    {
        "type":"object",
        "properties": { 
            "stock_code" :
                        {
                            "type":"string" , 
                            "description" : "a unique code which tell stock information for a particular stock price"
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

user_input ="give me stock related information for TCS  stock code"
response = client.responses.create(model="gpt-5.0-luna", input = user_input , tools = my_tools)


llm_output=response.output 
print(llm_output)
print("======================================================================")

print(response.output_text)

## it will be having some parts where it mght be making calls to the functions 
tools_output=[]
while True:
    pass
