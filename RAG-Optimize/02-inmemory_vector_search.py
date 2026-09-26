import os
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import CrossEncoder
from langchain_core.vectorstores import InMemoryVectorStore

load_dotenv()

documents = [
    "I need to complete this assignment by tomorrow evening.",
    "I must wrap up this task before tomorrow night.",
    "My goal is to finish this project by tomorrow afternoon.",
    "I have to get this work done by tomorrow end of day.",
    "I need to finalize this project by tomorrow night.",
    "I should have this task completed before tomorrow evening.",
    "I need to deliver this work by the end of tomorrow.",
    "I plan to finish up this project by tomorrow evening.",
    "I must have this assignment wrapped up by tomorrow night.",
    "I have to conclude this project before tomorrow evening ends."
]


def get_embedding(docs):
    client = OpenAI()
    response = client.embeddings.create(
        model="text-embedding-3-small", input=docs, dimensions=300)
    embeds = []
    for e in response.data:
        embeds.append(e.embedding)

    return embeds


embedding = get_embedding(documents)
store = InMemoryVectorStore(embedding)

user_query ="I have to conclude this project before tomorrow evening ends."
user_embedding = get_embedding(user_query)[0]
result = store.similarity_search_by_vector(embedding = user_embedding)

print(result)

