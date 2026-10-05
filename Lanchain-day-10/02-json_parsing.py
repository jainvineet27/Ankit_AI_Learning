from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

# 1. Output ka schema define karein


class Person(BaseModel):
    first_name: str = Field(description="The first name of the person")
    last_name: str = Field(description="The last name of the person")


# 2. Model & Parser initialize karein
model = ChatOpenAI(model="gpt-5.6-luna", temperature=0)
parser = JsonOutputParser(pydantic_object=Person)

# 3. Prompt mein format instructions inject karein
prompt = PromptTemplate(
    template="Extract the first name and last name from the provided input: {name}.\n{format_instructions}",
    input_variables=["name"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()},
)

# 4. Chain: Prompt -> Model -> Parser Instance
chain = prompt | model | parser

# 5. Invoke
result = chain.invoke({"name": "vineet jain"})

print(result)
# Output type: dict
# {'first_name': 'vineet', 'last_name': 'jain'}
print(result["first_name"])  # 'vineet'
