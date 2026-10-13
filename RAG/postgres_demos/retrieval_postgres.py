from dotenv import load_dotenv

from openai import OpenAI
from sqlalchemy import create_engine
import pandas as pd

from ingestion_postgres import get_embeddings_batch

load_dotenv()

client = OpenAI()
engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


def execute_query(query, params=None):
    with engine.begin() as conn:
        df = pd.read_sql(query, conn)
    return df


user_query = "How many days of Earned Leave are regular employees entitled to in a calendar year?"

user_embedding = get_embeddings_batch([user_query])[0]

sql_query = f"""
select * 
from public.hr_policy_docs
order by  embedding <=> '{user_embedding}' 
limit 10
"""
# --- closest to the user query based on embedding similarity  we would be getting the results ...

results_df = execute_query(sql_query)
results_content = results_df['content']
prompt = f'''
Kindly provide a summary of the following HR policy documents in bullet points.
based on the provided user query : {user_query}
and the retrieved context: {results_content}


Do not assume any information that is not present in the retrieved context.
Ensure that the summary is concise and directly addresses the user query.
'''
response = client.responses.create(model="gpt-5.6-luna",
                                   input=prompt)

print(response.output_text)
