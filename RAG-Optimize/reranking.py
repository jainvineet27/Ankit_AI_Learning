from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

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


def rerank(documents,  query, top_n=3):

    pairs = [[query, doc] for doc in documents]

    reranker = CrossEncoder(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2")
    scores = reranker.predict(pairs)
    print(scores)
    new_output = sorted(zip(scores, documents),
                        key=lambda x: x[0], reverse=True)
    top_docs = [doc for out, doc in new_output][:3]

    return top_docs


if __name__ == "__main__":
    query = "I need to complete this assignment by tomorrow evening."
    reranked_output = rerank(documents, query, top_n=3)
    print(reranked_output)
