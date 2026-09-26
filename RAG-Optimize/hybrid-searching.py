from openai import OpenAI
from reranking import rerank
from bm25_keyword_search import keyword_search
from dotenv import load_dotenv


load_dotenv()
client = OpenAI()

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

if __name__ == "__main__":
    query = "finish my work by tomorrow "
    keywords_output = keyword_search(documents, query=query, top_n=5)
    vector_docs = documents[:5]

    ''' to find the unique only documents ..... '''

    combine_docs = list(set(keywords_output + vector_docs))

    final_output = rerank(documents=combine_docs, query=query, top_n=3)

    print(final_output)
