''' ====================================          Embeddings Demo'''
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
load_dotenv()

client = OpenAI()
documents = ["spark is a distirbuted computed enginee", "star schema combinaiton of fact and dimension",
             "power bi is a microsfot product ", "RAG represents retrieval augement genration", "VIral kohli is world class batsman"]


def get_embeddings(document: str) -> List[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small", input=document, dimensions=4)

    return response.data[0].embedding


all_embeddings = []
for doc in documents:
    embedding = get_embeddings(doc)
    all_embeddings.append(embedding)

for doc, embedding in zip(documents, all_embeddings):
    print(f'doc -->{doc} and its embedding --> {embedding}')


chroma_client = chromadb.Client()

if chroma_client.get_or_create_collection("demo1"):
    chroma_client.delete_collection("demo1")

collection = chroma_client.get_or_create_collection(
    name="demo1", metadata={"hnsw:space": "cosine"})
n = len(documents)
ids = [f"id_{i}" for i in range(n)]

collection.add(ids=ids, documents=documents, embeddings=all_embeddings)

# 4. Generate a 4-dim embedding for your query text
query_text = "Hey tell me about the spark or apache spark"
query_vector = get_embeddings(query_text)


result = collection.query(
    query_embeddings=query_vector, n_results=2)

print(result)
print("===============================================")
print(f'{result.get("documents", '')}')

distances = [1-item for x in result.get("distances", "") for item in x]
print("distances", distances)
