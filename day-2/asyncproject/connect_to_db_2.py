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
    '''
    Use this function to extract the column names and their data types for a supplied table 
    args :  schema name and  table name 
    output : it returns the entire  schema of the table corresponding to the name of table , column names and data types.
    '''
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
    '''
    Use this function or method in order to identify whether the tables has been present into the database or not 
    If yes then using these tables call another function to identify the corresponding schema of that table 
    args  schema name and the table name 
    '''
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
