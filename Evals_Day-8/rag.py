from deepeval.models import OpenAIModel
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, ContextualRecallMetric, ContextualPrecisionMetric
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
import random
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

from chromadb import PersistentClient
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from goldendataset import read_golden_datset

from sentence_transformers import CrossEncoder

from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi
import re

load_dotenv()

stemmer = PorterStemmer()
# EVAL_MODEL = "gpt-5.6-luna"

EVAL_MODEL = OpenAIModel(
    model="gpt-5.4-nano",
    temperature=0
)
reranker = CrossEncoder(
    model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2")


client = OpenAI()
cr_client = PersistentClient("./chromadb")
collection = cr_client.get_or_create_collection("rag_collection")


def preprocess(doc):
    clean = re.sub(r"[^\w\s]", "", doc).strip().lower()
    tokenized_doc = stemmer.stem(clean).split(" ")

    return tokenized_doc


def best_matching(query, documents, top_k=3):
    tokenized_document_list = []
    for doc in documents:
        tokenized_document = preprocess(doc)
        tokenized_document_list.append(tokenized_document)

    bm25 = BM25Okapi(tokenized_document_list)
    tokenzied_query = preprocess(query)

    scores = bm25.get_scores(tokenzied_query)

    print("BM25", scores)
    result = sorted(zip(scores, documents),
                    key=lambda x: x[0], reverse=True)

    final = [item[1] for item in result]

    return final


def create_embeddings(chunks, dimension=300):
    response = client.embeddings.create(
        model="text-embedding-3-small", input=chunks, dimensions=dimension)

    embeds = []
    for item in response.data:
        embeds.append(item.embedding)

    return embeds


def chunk_ingestion(source_folder=None):
    if not source_folder:
        source_folder = "source"
    chunks_list = []
    metadatas = []
    ids = []

    parent_cwd = os.path.dirname(__file__)
    target_folder = os.path.join(parent_cwd, source_folder)
    if os.listdir(target_folder):
        for file in os.listdir(target_folder):
            file_path = os.path.join(target_folder, file)
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=140, separators=["\n\n", "\n", " ", "."])
            chunks = splitter.split_documents(documents)

            print("len of chunks ", len(chunks))
            print("sample chunks >>>>>>>>>>>>>>  ", chunks[0].page_content)

            if chunks:
                for chunk in chunks:
                    text_content = chunk.page_content
                    chunks_list.append(text_content)
                    chunk_id = str(uuid.uuid4()) + str(random.randint(1, 1000))
                    ids.append(chunk_id)
                    metadatas.append(chunk.metadata)

    print("Chunks are being generated succesfully ,,,,, ", len(ids))

    return chunks_list, metadatas, ids


def ingest_into_vector_db(chunks, metadatas, ids, embeddings):
    print("inside vector ingestions")

    collection.add(ids=[str(uuid.uuid4()) for i in range(len(embeddings))], embeddings=embeddings,
                   metadatas=metadatas, documents=chunks)

    print("Information has been added succesfully ...")


def retrieve_information(query_embeddings, top_k=20):
    print("inside the fetching information from retrieval ")

    results = collection.query(
        query_embeddings=query_embeddings, n_results=top_k)
    # print(results.get("documents"))
    print("information is retrieved successfully.. ")
    return results.get("documents", "")
    # list of list will be returned ....


def return_actual_ouput(query, retrieved_context):
    prompt = f"""
    Based on the user input Kindly help to provide the answer 
    user asked {query}

    retrieved context  : {retrieved_context}    
    Ensure that the summary is concise and directly addresses the user query.
    Keep the answer limit  upto 15-25 words. 
    """

    response = client.responses.create(model="gpt-5.6-luna", input=prompt)

    return response.output_text


def re_ranking(query, documents, top_k=3):

    pairs = [[q, context] for q, context in zip(query, documents)]

    scores = reranker.predict(pairs)

    print(scores)
    new_output = sorted(zip(scores, documents),
                        key=lambda x: x[0], reverse=True)
    top_docs = [doc for out, doc in new_output][:top_k]

    return top_docs


chunks, metadata, ids = chunk_ingestion()
embeddings = create_embeddings(chunks, 300)
ingest_into_vector_db(chunks, metadata, ids, embeddings)
queries, expected_output_list = read_golden_datset()


test_case_list = []
for i in range(len(queries)):
    query = queries[i]
    expected_output = expected_output_list[i]
    query_embedding = create_embeddings(query, 300)[0]

    retrieved_context = [sub_item for item in retrieve_information(
        query_embeddings=query_embedding) for sub_item in item]

    top_bm_documents = best_matching(query, retrieved_context, 5)
    rerank_retrieved_context = re_ranking(query, top_bm_documents, 3)

    actual_output = return_actual_ouput(query, rerank_retrieved_context)

    test_case = LLMTestCase(
        expected_output=expected_output,
        actual_output=actual_output,
        input=query,
        retrieval_context=rerank_retrieved_context

    )

    test_case_list.append(test_case)

recall_context = ContextualRecallMetric(threshold=.7, model=EVAL_MODEL)
precision_context = ContextualPrecisionMetric(threshold=.7, model=EVAL_MODEL)

answer_relevancy = AnswerRelevancyMetric(threshold=.7, model=EVAL_MODEL)
faithfulness = FaithfulnessMetric(
    threshold=.7, model=EVAL_MODEL)


result = evaluate(test_cases=test_case_list, metrics=[
                  answer_relevancy, faithfulness, recall_context, precision_context])
