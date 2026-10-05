from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model='gpt-5.6-luna')

prompt = PromptTemplate(
    template="Say  {input} in {output_language} language ")

chain = prompt | llm | StrOutputParser()

response = chain.invoke(
    {"input": "hey how are you doing ",
     "output_language": "Dutch"}
)

print(response)
