from dotenv import load_dotenv
from openai import OpenAI
from typesafe_sdk import TypeSafeClient
from typesafe_sdk import Noul, NoulCriteria, Choice, Score
import os
import json
import requests
import pandas as pd
import numpy as np


load_dotenv()

jev_client = TypeSafeClient()
client = OpenAI()

choice_criteria = {
    "technology": "python , spark , cloud , infrastructure, sql , java",
    "nature": "flowers trees root , rainbow sushine",
    "robotics": "computer robotics , machinery ",
    "art": "pcitures , canvas paintings",
    "abstract": "some random  arts or pciture or gallery metro  or subways ",
    "wildlife": "animal zoology"
}

score_criteria = [
    "sev 1 : dissatsifed ",  "sev 2  : neutral", " sev 3 : satisfied happy and content"
]

user_query_1 = "How many leave can be carry forward in a year"
user_query_2 = "why spark is lazy ,how lazy loading and cache and persist works "

spark_sentences = [
    "Apache Spark is an open-source, distributed computing system designed for fast processing of large-scale datasets.",
    "It was originally developed at UC Berkeley's AMPLab in 2009 and later donated to the Apache Software Foundation.",
    "Unlike Apache Hadoop MapReduce, Spark processes data primarily in-memory (RAM), making it up to 100 times faster for certain workloads.",
    "The core building block of Spark is the Resilient Distributed Dataset (RDD), a fault-tolerant collection of data partitioned across cluster nodes.",
    "Spark provides high-level APIs in multiple programming languages, including Python (PySpark), Scala, Java, and R.",
    "Spark SQL allows developers to query structured data using standard SQL syntax alongside DataFrames and Datasets.",
    "For real-time applications, Spark Streaming and Structured Streaming process continuous streams of incoming data with low latency.",
    "MLlib is Spark's built-in machine learning library, offering scalable algorithms for classification, regression, clustering, and collaborative filtering.",
    "Spark includes GraphX, an API optimized for graph computation and graph-parallel analysis.",
    "It can run as an independent standalone cluster or integrate with resource managers like Kubernetes, Apache Mesos, and Hadoop YARN.",
]


# Build the state
state = {
    "user_query": user_query_1
}

for i, doc in enumerate(spark_sentences):
    key = f"C{i+1}"
    value = doc
    state[key] = value

questions = {
    "is_it_urgent": Noul(instructions="based on the user input can you please whether this is urgent"),
    "which_category": Choice(instructions="based on the user question which category it fall ins"),
    "rating": Score(instructions="based on user input determine the score based on following criteria", score_criteria=score_criteria)
}


response = jev_client.system_one(state=state, questions=questions)

for k, v in response.answers.items():
    print(k, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", v)
