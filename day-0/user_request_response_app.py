import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

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

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------------------------------------------------------
# 3. USER INPUT & EVENT TRIGGER
# ---------------------------------------------------------
user_input = st.chat_input("Ask a question (e.g., 'What is the total amount in transactions?')")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing schema and question..."):
            
            # Step A: Retrieve Schema
            table_schema = get_schema(schema_name="dbo", table_name="transactions")
            
            # Step B: Generate SQL or Flag Bad Input
            sql_prompt = f"""
            You are a SQL Server (T-SQL) expert.
            Table Schema:
            {table_schema}

            User Question: {user_input}

            Rules:
            1. If the question is valid and can be answered using the table schema, output ONLY the raw executable T-SQL query (e.g., starting with SELECT).
            2. Do NOT use markdown code fences (```sql or ```).
            3. If the user input is gibberish, meaningless, off-topic, or cannot be answered from the schema, output exactly: INVALID_INPUT
            """
            
            sql_response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=sql_prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            
            generated_output = sql_response.text.strip().replace("```sql", "").replace("```", "").strip()
            
            # Step C: Handle Bad Input vs Executable SQL
            if "INVALID_INPUT" in generated_output or not generated_output.upper().startswith(("SELECT", "WITH")):
                assistant_reply = "Sorry, I couldn't understand your question. Kindly try again with a question related to your transactions data."
                st.warning(assistant_reply)
            else:
                # Step D: Safe Execution
                try:
                    query_result = execute_query(generated_output)
                    
                    with st.expander("Generated SQL Query"):
                        st.code(generated_output, language="sql")
                    
                    assistant_reply = str(query_result)
                    st.write(assistant_reply)
                except Exception as e:
                    assistant_reply = f"Could not process the query: {e}"
                    st.error(assistant_reply)

        # Append assistant response to memory
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})