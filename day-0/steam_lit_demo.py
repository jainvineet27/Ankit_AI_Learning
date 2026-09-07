import streamlit as st
st.title("DATA gpt")
st.write("Helped to dientfiy the SQL statement based onthe user natural language output ")

if "messages" not in st.session.state:
    st.session.state["messages"]=[]


question =st.chat_input("Ask your questions :")
if question:
    print("Hello")
