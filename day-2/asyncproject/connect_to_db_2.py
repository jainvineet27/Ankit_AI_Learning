import pandas as pd
# import psycopg
from psycopg import *
from sqlalchemy import create_engine

# postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


def execute_query(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


async def get_schema(schema_name:str, table_name:str):
    query = f'''
            SELECT
    table_name ,       
    column_name,
    data_type
    FROM information_schema.columns
    where table_schema= '{schema_name}' and table_name = '{table_name}'
    ORDER BY ordinal_position;
        '''
    schema = execute_query(query)
    return schema


async def get_table(schema_name:str,table_name :str):
    query = f'''
            SELECT
    table_name ,  table_schema    
    FROM information_schema.columns
    where table_schema= '{schema_name}' and table_name = '{table_name}'
    ORDER BY ordinal_position;
        '''
    tables  =  execute_query(query)
    return tables


#result = execute_query("select * from orders limit 5")
# print(result)
#result = get_table('orders')
# print(result)
