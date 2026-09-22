from openai import OpenAI
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


def create_query(query:str):
    
    with engine.connect() as connection:
        # You can execute your query here using connection.execute()
        df = pd.read_sql(query, connection)
    return df 



def add_data(chunks ,embeddings):
    pass


def create_embedings():
    pass




