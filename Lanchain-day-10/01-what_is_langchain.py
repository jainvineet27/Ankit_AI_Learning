from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()

model = ChatOpenAI(model="gpt-5.6-luna")

prompt = PromptTemplate(
    template="hey help me explain about {topic} in couple 100 words")

str_parser = StrOutputParser()

prompt2 = PromptTemplate(
    template="based on the entire articles {artice} let us make 3-4 quiz type questions ")

chain = prompt | model | str_parser | prompt2 | model | str_parser


result = chain.invoke({"topic": "langfuse"})
print(result)
