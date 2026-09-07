import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Database helper functions from your mydb.py
from mydb import execute_query, get_schema

# ---------------------------------------------------------
# 1. SETUP & GEMINI CLIENT
# ---------------------------------------------------------
load_dotenv()
st.set_page_config(page_title="SQL Chatbot", page_icon="📊")
st.title("SQL Server Natural Language Assistant")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# 2. SESSION STATE (Chat Memory)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------------------------------------
# 3. CHAT & EXECUTION PIPELINE
# ---------------------------------------------------------
while True:
    user_input = st.chat_input("Ask a question (e.g., 'What is the total amount in transactions?')")
    if user_input=="" or user_input=="exit":
        break
    else:
            
        # 1. Append & render user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing schema and querying database..."):
                
                # Step A: Schema retrieve karein (Default: dbo.transactions)
                table_schema = get_schema(schema_name="dbo", table_name="transactions")
                
                # Step B: Gemini se clean SQL generate karwayein
                sql_prompt = f"""
                You are a SQL Server (T-SQL) expert.
                Table Schema:
                {table_schema}

                User Question: {user_input}

                Generate only the raw SQL query to answer this question.
                Do NOT include markdown formatting like ```sql or explanations. 
                Only output the pure SQL query.
                """
                
                sql_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=sql_prompt,
                    config=types.GenerateContentConfig(temperature=0.0)
                )
                
                generated_sql = sql_response.text.strip().replace("```sql", "").replace("```", "")
                
                # Step C: SQL execute karein
                try:
                    query_result = execute_query(generated_sql)
                    
                    # Step D: Final calculation / Natural language answer
                    summary_prompt = f"""
                    User Question: {user_input}
                    Executed SQL: {generated_sql}
                    SQL Result: {query_result}

                    Provide a clear, direct, and concise answer to the user based on the SQL result.
                    """
                    
                    final_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=summary_prompt,
                        config=types.GenerateContentConfig(temperature=0.2)
                    )
                    
                    assistant_reply = final_response.text
                    
                    # Show SQL & Answer
                    with st.expander("Show Generated SQL"):
                        st.code(generated_sql, language="sql")
                    st.write(assistant_reply)
                    
                except Exception as e:
                    assistant_reply = f"Error executing query: {e}"
                    st.error(assistant_reply)

        # 2. Append assistant message to memory
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})