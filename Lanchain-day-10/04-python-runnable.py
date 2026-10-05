from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from langchain_core.runnables import RunnableParallel, RunnableLambda
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()


class Person(BaseModel):
    name: str = Field(description="name of the person")
    age: int = Field(description="defined the age of the person")
    bmi: float = Field(
        description="represent the BMI of the person Body mass index")


model = ChatOpenAI(model='gpt-5.6-luna')

json_parser = JsonOutputParser(pydantic_object=Person)


def calculate_bmi(data):

    height = data["height"]
    weight = data["weight"]

    bmi = weight/(height*height)

    output = {**data, "bmi": bmi}

    return output


bmi_runnable = RunnableLambda(calculate_bmi)


p1 = PromptTemplate(
    template='''tell me its BMI with provided for following person
    Name  : {name} 
    Age : {age}
    Height : {height}
    Weight : {weight}
        
    return the response in json response with three attibutes name , age and BMI  
    
    {format_instructions} ''',
    input_variables=["height", "weight", "name", "age"],
    partial_variables={
        "format_instructions": json_parser.get_format_instructions()}

)


chain = bmi_runnable | p1 | model | json_parser

result = chain.invoke({"name": "vineet jain", "age": 31,
                      "height": 1.87, "weight": 92})


print(result)
