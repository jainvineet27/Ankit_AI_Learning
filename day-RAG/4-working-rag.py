import os
from chromadb import PersistentClient
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

load_dotenv()

chroma_client = PersistentClient(path="./chromadb")
collection = chroma_client.get_or_create_collection(
    name="dump", metadata={"hnsw:space": "cosine"}
)
client = OpenAI()


def read_document():
    documents_list = []
    search_root = "."
    folder_name = "source"
    for root, dirs, files in os.walk(search_root):
        if folder_name in dirs:
            found_path = os.path.join(root, folder_name)
            print("Folder mil gaya:", os.path.abspath(found_path))
            break  # Pehla match milte hi ruk jao

    if not os.path.isdir(folder_name):
        raise FileNotFoundError(f"{folder_name} is not found")

    for file in os.listdir(folder_name):
        if file.endswith(".pdf"):
            file_path = os.path.abspath(os.path.join(folder_name, file))
            print("Processing file:", file_path)
            loader = PyMuPDFLoader(file_path)
            documents_list.append(loader.load())

    return documents_list


def create_chunks(documents_list):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", " ", "."]
    )
    chunks_data, metadatas, ids = [], [], []

    for documents in documents_list:
        chunks = splitter.split_documents(documents)
        for i, chunk_obj in enumerate(chunks):
            chunk_text = chunk_obj.page_content
            raw_path = chunk_obj.metadata.get(
                "file_path", ""
            )
            file_name = os.path.basename(raw_path)
            print("file name >>>>>>>>>>>", file_name)

            chunks_data.append(chunk_text)
            metadatas.append({"file_name": file_name})
            ids.append(f"chunk_{file_name}_{i}")

    return chunks_data, metadatas, ids


def create_batch_embeddings(chunks, dimensions=300):
    response = client.embeddings.create(
        model="text-embedding-3-small", input=chunks, dimensions=dimensions
    )
    return [item.embedding for item in response.data]


def ingestion_into_vdb(collection, embeddings, documents, metadatas, ids):
    collection.add(
        ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
    )


def similarity_search(user_embedding, top_k=3):
    return collection.query(query_embeddings=user_embedding, n_results=top_k)


if __name__ == "__main__":
    docs = read_document()
    chunks, metadatas, ids = create_chunks(docs)

    embeddings = create_batch_embeddings(chunks)
    ingestion_into_vdb(collection, embeddings, chunks, metadatas, ids)

    user_query = "Explain me about Termination and maternity policy in bullet points in 50 word each"
    user_embedding = create_batch_embeddings([user_query])
    search_results = similarity_search(user_embedding, top_k=3)

    # Retrieved chunk texts extract kar rahe hain prompt ke liye
    ''' result.get("documents") -->  list of list for x in lsitof list make a new list ... read make a string ... '''

    retrieved_context = "\n".join(search_results["documents"][0])

    prompt = f"""
    Kindly answer based on the user input.
    User question: {user_query}
    
    Retrieved Context:
    {retrieved_context}
    
    Rule: Answer only based on the provided context in natural language.
    Do not hallucinate.
    """

    response = client.responses.create(
        model="gpt-5.6-luna", input=prompt)

    print(response.output_text)
