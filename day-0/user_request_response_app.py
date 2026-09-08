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
            4. Do no allow user to make the DELETE , UPDATE , DROP , TRUNCATE , INSERT request the information in the tables ,output exactly: INVALID_INPUT  
            """
            
            sql_response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=sql_prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            
            generated_output = sql_response.text.strip().replace("```sql", "").replace("```", "").strip()
            print(generated_output)
            
      # ... (inside your user_input block under "assistant")

            if "INVALID_INPUT" in generated_output or not generated_output.upper().startswith(("SELECT", "WITH")):
                assistant_reply = "Sorry, I couldn't understand your question. Kindly try again with a question related to your transactions data."
                st.warning(assistant_reply)
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": assistant_reply})
            else:
                try:
                    # Step 1: Run query and get DataFrame
                    df_result = execute_query(generated_output)
                    
                    # Step 2: Show SQL query in expander
                    with st.expander("Generated SQL Query"):
                        st.code(generated_output, language="sql")
                    
                    # Step 3: Display entire output in Streamlit UI
                    if df_result.empty:
                        st.info("Query executed successfully, but returned 0 rows.")
                        st.session_state.messages.append({"role": "assistant", "type": "text", "content": "No rows returned."})
                    else:

                        st.write(f"**Found {len(df_result)} record(s):**")
                        print(">>>>>>>>>>>>>>> ",len(df_result))
                        st.dataframe(df_result, use_container_width=True)
                        
                        # Step 4: CSV Download Button
                        csv_data = df_result.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Report as CSV",
                            data=csv_data,
                            file_name="query_report.csv",
                            mime="text/csv",
                            key="download_csv_current"
                        )
                        
                        # Save into memory so it stays visible across runs
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "type": "dataframe", 
                            "content": df_result
                        })
                        
                except Exception as e:
                    error_msg = f"Could not process the query: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "type": "text", "content": error_msg})