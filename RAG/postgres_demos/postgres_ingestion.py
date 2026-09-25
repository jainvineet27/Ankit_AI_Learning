#from chunking import create_chunks
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from langchain_core.documents import Document
from sqlalchemy.sql import text
#postgresql+psycopg://USERNAME:PASSWORD@HOST:PORT/DATABASE

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

load_dotenv()

client = OpenAI()


def create_chunks(source_folder=None, chunk_size=500, chunk_overlap=100):
    metadatas=[]
    chunks_data=[]
    ids=[]
    #to find the current file path 
    source_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "source"))

    if os.path.isdir(source_folder):

        for file in os.listdir(source_folder):
            file_path = os.path.join(source_folder, file)
            reader=  PdfReader(file_path)
            
            documents=[] 
            for page_num , page in enumerate(reader.pages):
                text= page.extract_text()
                if text:
                    doc=Document(page_content=text, metadata={"source": file_path, "page": page_num})
                    documents.append(doc)

                
            # Process each file as  needed
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100,separators=["\n\n", "\n", " ","."])
            chunks = splitter.split_documents(documents)
            for chunk in chunks:
                chunks_data.append(chunk.page_content)
                metadatas.append({"source": file_path})
                ids.append(f"{file_path}_{chunk.id}")


    return chunks_data, ids, metadatas

def get_embeddings_batch(chunks):
    if not chunks:
        print("No chunks found...")
        return []
    
    response = client.embeddings.create(model='text-embedding-3-small',
                            input= chunks,
                            dimensions=300)
    embeds = []
    for item in response.data:
        embedding = item.embedding
        embeds.append(embedding)
    return embeds


def add_data(chunks, embeddings):
      # Sahi list comprehension (no data.append with generator):
    data = [
        {"content": chunk, "embedding": str(embedding)}
        for chunk, embedding in zip(chunks, embeddings)
    ]    
    
    query = text("""
                INSERT INTO public.hr_policy_docs
                    (content, embedding)
                VALUES
                    (:content, :embedding)
            """)    
    
    try: 
        with engine.begin() as conn:
            conn.execute(query, data)
        print(f"Inserted {len(data)} chunks successfully into database!")
    except Exception as e:
        print(f"Error inserting chunk: {e}")

    print(f"Inserted chunk successfuly ....")
        
                        
chunks, ids, metadatas = create_chunks(source_folder=None, chunk_size=500, chunk_overlap=100)
print(len(chunks))
embeddings = get_embeddings_batch(chunks)

add_data(chunks, embeddings)
