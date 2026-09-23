#from chunking import create_chunks
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import text
import psycopg
from sqlalchemy import create_engine
import os 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader

#postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

load_dotenv()

client = OpenAI()


def create_chunks(source_folder="source", chunk_size=500, chunk_overlap=100):
    metadatas=[]
    chunks_data=[]
    ids=[]
    if os.path.isdir(source_folder):
        for file in os.listdir(source_folder):
            file_path = os.path.join(source_folder, file)
            loader=  PyMuPDFLoader(file_path)
            documents = loader.load()
            # Process each file as  needed
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100,separators=["\n\n", "\n", " ","."])
            chunks = splitter.split_documents(documents)
            for chunk in chunks:
                chunks_data.append(chunk.page_content)
                metadatas.append({"source": file_path})
                ids.append(f"{file_path}_{chunk.id}")


    return chunks_data, ids, metadatas

def get_embeddings_batch(texts):
    response = client.embeddings.create(model='text-embedding-3-small',
                            input= texts,
                            dimensions=300)
    embeds = []
    for item in response.data:
        embedding = item.embedding
        embeds.append(embedding)
    return embeds


def add_data(chunks, embeddings):
    for chunk, embedding in zip(chunks, embeddings):
        query = text("""
            INSERT INTO hr_policy_docs
                (content, embedding)
            VALUES
                (:content, :embedding)
        """)
        # : content ye placeholder hota hai ....  sae  . kal ko ' ya '  ayega isliye f {} ko avoid kiaa ..
    # Prepare all parameters in a single list
        data = [{"content": chunk, "embedding": str(embedding)}      for chunk, embedding in zip(chunks, embeddings)]
        
        with engine.begin() as conn:
            conn.execute(
                query, data               
            )


chunks, ids, metadatas = create_chunks(source_folder="source", chunk_size=500, chunk_overlap=100)
embeddings = get_embeddings_batch(chunks)

add_data(chunks, embeddings)