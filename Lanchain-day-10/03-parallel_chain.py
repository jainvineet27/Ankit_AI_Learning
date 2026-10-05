from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
model = ChatOpenAI(model="gpt-5.6-luna")


class Poem(BaseModel):
    title: str = Field(description="tell about poem title")
    description: str = Field(description="this is actual poem")


class Joke(BaseModel):
    title: str = Field(description="tell about title of the joke ")
    description: str = Field(description="this is actual joke")


'''
Is code mein kya errors hain?
JsonOutputParser(Joke) galat syntax hai (Runtime Error):
JsonOutputParser positional argument directly accept nahi karta. Isko keyword argument chahiye:
❌ JsonOutputParser(Joke)
✅ JsonOutputParser(pydantic_object=Joke)
'''
'''
Model sochta hai:

"User ne joke manga hai → normal text mein joke de deta hoon."

Parser sochta hai:

"Mujhe JSON chahiye."

💥 Conflict → OutputParserException
'''


joke_parser = JsonOutputParser(pydantic_object=Joke)
poem_parser = JsonOutputParser(pydantic_object=Poem)

p1 = PromptTemplate(
    template="tell me about the joke on {joke} return the output in the json only format  having only two field  title and description   ", input_variables=["joke"], partial_variables={"format_instructions": joke_parser.get_format_instructions()})
p2 = PromptTemplate(
    template="Tell me about the poem  on {poem} return the output in the json only format  having only two field  title and description ", input_variables=["poem"], partial_variables={"format_instructions": poem_parser.get_format_instructions()})


chain = RunnableParallel(joke=p1 | model | joke_parser,
                         poem=p2 | model | poem_parser)

result = chain.invoke({"joke": "bollywood films", "poem": "Sun"})

print(result)
