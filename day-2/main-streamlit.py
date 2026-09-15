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

tools  =[
{
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
user_input ="giv me top 10 sales"
response = client.responses.create(model="gpt-5.0-luna", input = user_input , tools = my_tools)


llm_output=response.output 
## it will be having some parts where it mght be making calls to the functions 
tools_output=[]
while True:
    pass
