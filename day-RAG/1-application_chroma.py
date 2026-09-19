from openai import OpenAI
from dotenv import load_dotenv
import chromadb

load_dotenv()
chroma_client = chromadb.Client()

# chroma_client.get_or_create_collection
# chroma_client.get_collection
# chroma_client.count_collections
collection = chroma_client.get_or_create_collection(name="demodb")
collection.add(
    ids=["id1", "id2"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ]
)
# chroma_client.delete_collection
output = collection.query(query_texts="tell me about oranges", n_results=1)
print(output)
collection = chroma_client.get_or_create_collection("abc")
'''
So think ki embeedding aur ids auto generate krna hai.. hume fir supply krne hai ..'''

# ollection.add(ids =[], embeddings=)
