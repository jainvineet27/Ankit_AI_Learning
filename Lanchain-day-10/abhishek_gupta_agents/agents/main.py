from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()


# create agent
# make basis python fucntion
# some more python gucntion using decaorator
# now use tavilty search as a tool
# researcch agent ocmplete

# iinput --------> agent[] <--> tools , memory  []  --> output


json_parser = JsonOutputParser()

llm = ChatOpenAI(model='gpt-5.6-luna')

prompt = PromptTemplate(
    template="Say  {input} in {output_language} language ")

chain = prompt | llm | json_parser
response = chain.invoke(
    {"input": "hey how are you doing ",
     "output_language": "Dutch"}
)

print(response)
