import streamlit as st
import asyncio
import json
import pandas as pd
from dotenv import load_dotenv
from openai import AsyncOpenAI

from orchestrator import concurrent_runs
from my_system_prompt import system_prompt
from connect_to_db_2 import execute_query

load_dotenv()

st.set_page_config(page_title="DataGPT - Agentic SQL", page_icon="📊", layout="wide")

# Tools definition
MY_TOOLS = [
    {
        "type": "function",
        "name": "get_stock_details",
        "description": "Provide information on the latest stock details based on user-provided stock code",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_code": {
                    "type": "string",
                    "description": "An NSE stock code provided by user input",
                }
            },
            "required": ["stock_code"],
        },
    },
    {
        "type": "function",
        "name": "get_schema",
        "description": "Provide information available schema required to address the question",
        "parameters": {
            "type": "object",
            "properties": {
                "schema_name": {
                    "type": "string",
                    "description": "Schema name (logical container of tables)",
                },
                "table_name": {
                    "type": "string",
                    "description": "Table name which stores actual data",
                },
            },
            "required": ["schema_name", "table_name"],
        },
    },
    {
        "type": "function",
        "name": "get_table",
        "description": "Provide table details matching user input questions",
        "parameters": {
            "type": "object",
            "properties": {
                "schema_name": {
                    "type": "string",
                    "description": "Schema name",
                },
                "table_name": {
                    "type": "string",
                    "description": "Table name",
                },
            },
            "required": ["schema_name", "table_name"],
        },
    },
]

# --- SESSION STATE INITIALIZATION ---
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []


async def run_agent_loop(user_input: str):
    """Executes the autonomous agent while loop with tool execution."""
    client = AsyncOpenAI()
    final_prompt = f"{system_prompt}\nUser question: {user_input}"
    logs = []

    response = await client.responses.create(
        model="gpt-5.6-luna",
        input=final_prompt,
        tools=MY_TOOLS,
    )
    response_id = response.id

    max_turns = 5
    turn = 0

    while turn < max_turns:
        turn += 1
        functions_calls = [item for item in response.output if item.type == "function_call"]

        if not functions_calls:
            logs.append(f"Turn {turn}: No further tools required. Exiting loop.")
            break

        logs.append(f"Turn {turn}: Model requested {len(functions_calls)} tool call(s).")
        for call in functions_calls:
            logs.append(f"Invoking `{call.name}` with `{call.arguments}`")

        # Execute tools concurrently
        tools_output = await concurrent_runs(functions_calls)
        logs.append(f"Tool execution completed.")

        # Send tool results back to the model
        response = await client.responses.create(
            model="gpt-5.6-luna",
            input=tools_output,
            previous_response_id=response_id,
        )
        response_id = response.id

    # Clean raw output from any Markdown ticks
    raw_sql = response.output_text.strip()
    cleaned_sql = raw_sql.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

    return cleaned_sql, logs


# --- UI LAYOUT ---
st.title("📊 DataGPT - Multi-Tool Agent")
st.caption("Ask questions in natural language. The agent gathers schema context via tools and runs the final SQL query.")

with st.form("query_form"):
    user_question = st.text_input(
        "Enter your question:",
        placeholder="Help me find number of courses and different course offerings and which department they belong to",
    )
    submitted = st.form_submit_button("Run Analysis", type="primary")

if submitted:
    if not user_question.strip():
        st.warning("Please enter a question before running.")
        st.stop()

    with st.spinner("Agent is inspecting schemas, running tools, and generating SQL..."):
        try:
            # Run the async agent loop inside Streamlit
            generated_sql, execution_logs = asyncio.run(run_agent_loop(user_question))
            query_results = execute_query(generated_sql)

            # Persist output to Session State
            st.session_state.last_query = generated_sql
            st.session_state.last_result = query_results
            st.session_state.agent_logs = execution_logs

        except Exception as err:
            st.error("Error executing agent loop or database query.")
            st.exception(err)
            st.stop()

# --- SEPARATE DISPLAY CONTAINERS (Rendered from Session State) ---
if st.session_state.last_query:
    # 1. Agent Trace Logs Expander
    with st.expander("🔍 View Agent Tool-Calling Trace", expanded=False):
        for log in st.session_state.agent_logs:
            st.write(log)

    # 2. Container: Generated SQL Query
    with st.container(border=True):
        st.subheader("📝 Generated SQL Query")
        st.code(st.session_state.last_query, language="sql")

    # 3. Container: Database Query Result
    with st.container(border=True):
        st.subheader("📋 Query Output")
        result_data = st.session_state.last_result

        if isinstance(result_data, pd.DataFrame):
            st.dataframe(result_data, use_container_width=True, hide_index=True)
            st.caption(f"{len(result_data):,} row(s) returned")
        elif isinstance(result_data, list) and len(result_data) > 0:
            df = pd.DataFrame(result_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"{len(df):,} row(s) returned")
        else:
            st.info("Query executed successfully, but no records were returned.")