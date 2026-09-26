from rank_bm25 import BM25Okapi
import re
from nltk.stem import PorterStemmer


stemmer = PorterStemmer()
output = stemmer.stem("... ranked")

out = re.sub(r"[^ \w\s]", "", output).strip().split(" ")
print(out, ">>>>>>>>>>>>>>>>>>>>>>> ")


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

# clean kia aur stemming nikaalal   --> preprocess ing m


def preprocess(doc):
    clean_docs = re.sub(r"[^\w\s]", "", doc)
    out = stemmer.stem(clean_docs).split(" ")
    return out


def get_tokenize_documents(documents):
    tokenized_documents = []
    for doc in documents:
        tokenized_documents.append(preprocess(doc))
    # print(tokenized_documents)

    return tokenized_documents


def keyword_search(tokenized_documents, query, top_n=3):

    bm_25 = BM25Okapi(tokenized_documents)
    tokenized_quer = preprocess(query)

    print("Length of  each documents >>>>> ", bm_25.doc_len)

    scores = bm_25.get_scores(tokenized_quer)

    new_list = sorted(zip(documents, scores),
                      key=lambda x: x[1], reverse=True)[:top_n]
    output = [item[0] for item in new_list]

    return output


''' 
Now I will be senidng this  retrie vdoucments from BM2 5 sapproach key word apprahc and the 
and rernaking appaoa
'''

if __name__ == "__main__":
    tokenized_documents = get_tokenize_documents(documents)
    query = "I plan to finish up this project by tomorrow evening."

    output = keyword_search(tokenized_documents, query, top_n=3)
    print(output)
