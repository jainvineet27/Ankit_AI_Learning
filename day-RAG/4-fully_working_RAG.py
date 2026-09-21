from dotenv import load_dotenv
from openai import OpenAI
import json
import re
import os
import requests
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection

load_dotenv()

print("Let us begin the applications ")

chroma_client = PersistentClient(path="./chromadb")
collection = chroma_client.get_or_create_collection(
    "dump", configuration={"hnsw": {"space": "cosine"}})
client = OpenAI()


def read_document():
    folder_name = "source"
    if os.path.isdir(folder_name):
        for file in os.listdir(folder_name):
            f_path = os.path.join(folder_name, file)
            file_path = os.path.abspath(f_path)

            print(">>>>>>>>>>>", file_path)
            if file.endswith(".pdf"):
                loader = PyMuPDFLoader(file_path)
                documents = loader.load()
                return documents
    else:
        raise FileNotFoundError(f"{folder_name} is not found")


def create_chunks(documents: Document):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", " ", "."])
    chunks = splitter.split_documents(documents)
    metadatas = []
    ids = []
    chunks_data = []

    if chunks:
        print("No. of chunks found in the documents", len(chunks))
        for i, chunk in enumerate(chunks):
            chunk = chunks[i].page_content
            chunks_data.append(chunk)
            metadata = chunks[i].metadata
            metadatas.append(metadata)
            id = f"chunk_{i}"
            ids.append(id)
    return chunks_data, metadatas, ids


def create_batch_embeddings(chunks, dimensions=300):
    response = client.embeddings.create(
        model='text-embedding-3-small', input=chunks, dimensions=dimensions)

    return [item.embedding for item in response.data]


def ingestion_into_vdb(collection, embeddings, metadatas, ids):
    print("======================= calling vector ingestions ====================== ")
    collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)


def similarity_search(collection: Collection, user_embedding):
    print("===================================================Perform similarity search========================================")
    result = collection.query(query_embeddings=user_embedding, n_results=3)

    print(result.get("data", ""))
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(result)
    return result


'''============== Function callings  '''
if __name__ == "__main__":
    documents = read_document()
    chunks, metadatas, ids = create_chunks(documents)
    # print(chunks)
    embeddings = create_batch_embeddings(chunks)
    ingestion_into_vdb(collection, embeddings, metadatas, ids)
    user_query = "Explain me about maternity leaves , how many weeks as mentionedi in the doucment "
    user_embedding = create_batch_embeddings(user_query)
    context = similarity_search(collection, user_embedding)

    prompt = f'''
    Based on the user input Kindly answer 
    user questions : {user_query}
    
    Retrieved Similar Context : {context}
    
    Rule: Kindly answer based on the provided context in the nautural language 
    Do not make up any response if no information is found.
    '''

    response = client.responses.create(model="gpt-5.6-luna", input=prompt)
    print(response.output_text)
