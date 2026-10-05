from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from langchain_core.tools import tool

from langchain_core.agents import create_agents

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model='gpt-5.6-luna')

# To install: pip install tavily-python

tavily_client = TavilyClient()


@tool
def web_search(query: str):
    response = tavily_client.search(
        query=query
        search_depth="advanced"
    )
    print(response)


# create an agent
# make norma python method
# make a mehtod with decorator
# tarvil method
# fuse with the langfuse
