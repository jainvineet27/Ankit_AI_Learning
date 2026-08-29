import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. SETUP & GEMINI CLIENT INITIALIZATION
# ---------------------------------------------------------
st.set_page_config(page_title="RAG Chatbot", page_icon="💬")
st.title("Document RAG Chat")

# Google GenAI Client initialize karein
# (Aap API key yahan pass kar sakte hain ya environment variable GEMINI_API_KEY use kar sakte hain)
#API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
load_dotenv() 
api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)


# ---------------------------------------------------------
# 2. VECTOR RETRIEVAL FUNCTION (Placeholder / Integration Point)
# ---------------------------------------------------------
def retrieve_relevant_chunks(query: str) -> str:
    """
    Aapka chunking aur vector database (FAISS/Chroma) ka code yahan aayega.
    Yeh function user query ke basis par matched context return karega.
    """
    # Example / Mock retrieved chunks:
    # vector_db = st.session_state.get("vector_db")
    # docs = vector_db.similarity_search(query, k=3)
    # return "\n\n".join([doc.page_content for doc in docs])
    
    # mock_context = """
    # Document Extract:
    # - Return policy: 30 days ke andar returns allow hain.
    # - Refund timeline: 5-7 business days lagte hain account mein aane mein.
    # - Shipping: Orders 24 ghante ke andar dispatch hote hain.
    # """
    response = client.models.generate_context(models = "gemini-3.5-flash",contents= query)

    mock_context = f"""
    Retrieved Context from Model:
    {response.text}
        """
    return mock_context


# ---------------------------------------------------------
# 3. SESSION STATE (Chat Memory)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# 4. RENDER CHAT HISTORY
# ---------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ---------------------------------------------------------
# 5. USER INPUT & GENAI RESPONSE PIPELINE
# ---------------------------------------------------------
user_input = st.chat_input("Apne document ke bare mein sawal poochein...")

if user_input:
    # Step A: User message show aur save karein
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Step B: Vector DB se relevant context retrieve karein
   # retrieved_context = retrieve_relevant_chunks(user_input)

    # Step C: Gemini Model se response generate karein
    with st.chat_message("assistant"):
        with st.spinner("Thinking & reading context..."):
            # Grounded prompt create karein
            prompt = f"""
        Neeche diye gaye context ke aadhar par user ke sawal ka answer karein.
        Agar context mein answer nahi hai, toh saaf bata dein.
            
                User Question:
                {user_input}
                """
            # Gemini 2.5 Flash call
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )
            
            assistant_reply = response.text
            st.write(assistant_reply)

    # Step D: Assistant response ko memory mein save karein
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})