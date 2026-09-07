''' make the connection with sssms service '''

import urllib
import pandas as pd
from sqlalchemy import create_engine


# 1. Configuration variables
SERVER = 'DESKTOP-0V640EH'   # Your server name from SSMS
DATABASE = 'vineetdb'        # Your database name
DRIVER = 'ODBC Driver 17 for SQL Server'

# 2. Build connection string for Windows Authentication
# trusted_connection=yes tells SQL Server to use your current logged-in Windows account
conn_str = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

# 3. Create SQLAlchemy engine
params = urllib.parse.quote_plus(conn_str)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")


def execute_query(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

def get_schema(table_name,schema_name="dbo"):
    """ This functon is helpful in returning the schema and its columns """
    query  =  f'''
            SELECT COLUMN_NAME,     DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME='{table_name}' and TABLE_SCHEMA ='{schema_name}'
            order by ORDINAL_POSITION
    '''
    return execute_query(query)

print(get_schema("transactions"))

