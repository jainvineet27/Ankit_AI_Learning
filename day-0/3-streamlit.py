import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from connect_to_db import execute_query, get_schema

load_dotenv()
client = OpenAI()


st.set_page_config(page_title="DataGPT", page_icon="📊", layout="wide")
st.title("📊 DataGPT")
st.caption("Ask questions about your database in plain English.")

# 1. Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_data(show_spinner=False)
def load_table_schema(table_name: str):
    """Fetch and cache table schema on demand."""
    return get_schema(table_name)


def detect_table_name(question: str) -> str:
    """Ask LLM to identify the target table name from the question."""
    prompt = f"""Identify the most likely single database table needed to answer this question.
Question: {question}
Return ONLY the table name in lowercase, nothing else (e.g. orders, users, products)."""

    response = client.responses.create(
        model="gpt-5.6-luna", input=prompt)

    return response.output_text.strip().lower()


def generate_sql(question: str, table_name: str, schema_str: str) -> str:
    """Generate a SELECT query using the retrieved schema."""
    prompt = f"""Generate one PostgreSQL SELECT query for the question below.
Table: {table_name}
Schema:
{schema_str}

Return SQL only, without markdown fences or explanations.
Question: {question}"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt)

    raw_sql = response.output_text.strip()
    return raw_sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()


# 2. Render Existing Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.write(msg["content"])
        else:
            st.caption(f"**Target Table:** `{msg['table_name']}`")
            st.code(msg["sql"], language="sql")
            if msg.get("data") is not None:
                st.dataframe(msg["data"], hide_index=True)

# 3. User Input & Execution Flow
if prompt := st.chat_input("What would you like to know? (e.g., Show top 5 orders)"):
    # Display and record the user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Process and record the assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing request and querying database..."):
            try:
                # Step A: Detect table
                table_name = detect_table_name(prompt)

                # Step B: Fetch schema dynamically
                schema_df = load_table_schema(table_name)
                schema_text = schema_df.to_string(index=False)

                # Step C: Generate SQL & Run
                sql_query = generate_sql(prompt, table_name, schema_text)
                df_result = execute_query(sql_query)

                # Display in the current chat container
                st.caption(f"**Target Table:** `{table_name}`")
                st.code(sql_query, language="sql")
                st.dataframe(df_result, hide_index=True)

                # Step D: Append assistant reply to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "table_name": table_name,
                    "sql": sql_query,
                    "data": df_result
                })

            except Exception as e:
                st.error("Failed to process the question.")
                st.exception(e)
