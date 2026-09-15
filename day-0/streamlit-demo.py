import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.title("Welcom to the DATAGPT")
st.write("Kindly give the user question in plain english...")

client = OpenAI()

if "messages" not in st.session_state:
    st.session_state['messages'] = []

for msg in st.session_state.messages:
    st.write(msg["role"])
    st.write(msg["content"])


question = st.chat_input("Ask your questions")
if question:
    st.session_state.messages.append({"role":"user", "content":question})
    response = client.responses.create(model="gpt-5-nano", input=question)
    st.session_state.messages.append({"role":"assistant", "content":response.output_text})
    
