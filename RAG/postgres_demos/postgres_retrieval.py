import psycopg2
from dotenv import load_dotenv
  
from openai import OpenAI
from sqlalchemy import create_engine
import pandas as pd

from postgres_ingestion import get_embeddings_batch

load_dotenv()

client = OpenAI()
engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
) 

def execute_query(query, params=None):
    with engine.begin() as conn:
        df= pd.read_sql(query,conn)
    return df 

user_query = "give me top 10 maternity leaves infomration  in the form of bullet points"

user_embedding = get_embeddings_batch([user_query])[0]

sql_query = f"""
select * 
from public.hr_policy_docs
order by  embedding <=> '{user_embedding}' 
limit 10
"""
#--- closest to the user query based on embedding similarity  we would be getting the results ... 

results_df = execute_query(sql_query)
prompt = '''
Kindly provide a summary of the following HR policy documents in bullet points.
based on the provided user query : {user_query}
and the retrieved context: {results_df.to_dict(orient='records')}

Kindly provide the summary in bullet points.
Do not assume any information that is not present in the retrieved context.
Ensure that the summary is concise and directly addresses the user query.
'''
response = client.responses.create(model="gpt-5.6-luna", input=f"Summarize the following HR policy documents: {results_df.to_dict(orient='records')}")

print(response.output_text)