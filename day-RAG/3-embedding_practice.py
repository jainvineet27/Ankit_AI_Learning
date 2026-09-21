from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re
import requests
from pypdf import PdfReader
from typing import List
load_dotenv()


def read_file_give_me_output():
    file_name = "enterprise_policy.pdf"
    file_path = os.path.abspath(file_name)
    print(file_path)
    reader = PdfReader(file_path)
    file_text = ''
    for page in reader.pages:
        file_text += page.extract_text() + '\n'

    loader = PyMuPDFLoader(file_path=file_path)
    documents = loader.load()
    print(">>>>>>>>>>>>>>>>>>>     ", len(documents))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", ".", ""])
    chunks = splitter.split_documents(documents)
    print("Chunks ", len(chunks), chunks[0])
    return file_text


def using_while_loop_get_chunks(chunk_size=500, chunk_overlap=100, start=0, turn=1):
    print("Approach 1, using  while loop to get the chunks  ")
    chunk_size = 500
    chunk_overlap = 100
    start = 0
    chunks = []
    ids = []
    turn = 1
    metadatas = []
    while start < len(file_text):
        end = start + chunk_size
        chunk = file_text[start:end]
        metadata = {"chunk_no": turn, "file_name": file_name}
        id = f"id_{turn}"
        turn += 1
        ids.append(id)
        metadatas.append(metadata)
        chunks.append(chunk)
        start += chunk_size-chunk_overlap
    print(len(chunks), len(metadatas), len(ids))
    return chunks, metadatas, ids


def get_me_batch_embedddings(chunks: List) -> List:
    client = OpenAI()

    response = client.embeddings.create(
        model="text-embedding-3-small", input=chunks, dimensions=300)

    return response.data[0].embedding


o = get_me_batch_embedddings(["hello this is dil top pagal hai .."])

# 1 read_file_give_me_output
# give the source folder and it will be reading the entire context and return full text
# 2 using_while_loop_get_chunks
# 3 get_me_batch_embedddings
read_file_give_me_output()
