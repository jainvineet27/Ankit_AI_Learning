from dotenv import load_dotenv
from typesafe_sdk import (TypeSafeClient, Noul, NoulCriteria, Score, Choice)
from openai import OpenAI
import os
import pandas as pd

# find me present workign directoe
# read csv and return the list of review

load_dotenv()

jev_client = TypeSafeClient()

client = OpenAI()


def read_csv():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    print(current_folder)
    reviews = []

    for file in os.listdir(current_folder):
        if file.endswith(".csv"):
            print("found file", file)
            file_path = os.path.join(current_folder, file)

            df = pd.read_csv(file_path)
            print(df.columns)
            new_cols = [col.lower() for col in df.columns]
            df.columns = new_cols

            reviews = df['reviews'].to_list()

    return reviews


reviews = read_csv()

choice_criteria = {"battery": "reivew discussed about the battery and similar components",
                   "performance": "review mainly talk about performance, life ",
                   "price": "review mainly talks how much cost of the product ",
                   "camera": "reivew mainly how camera quality  is or mega pixels",
                   "other": "something other sor of feedback the review talks about "}

score_criteria = ["Dissatisifed", "Ok Normal",
                  "Good", "Very Good", "Exceptional /Outstanding"]


questions = {
    "is_camera_present": Noul(instructions="is the reivew talks about camera",
                              criteria=NoulCriteria(true="if the review talks about the camera quality", false="if the review do not talk camera")),
    "is_battery_present": Noul(instructions="is the reivew talks about batter", criteria=NoulCriteria(true="if the review talks about the battery quality", false="if the review do not talk battery")),
    "is_price_present": Noul(instructions="is the reivew talks about price", criteria=NoulCriteria(true="if the review talks about the price price", false="if the review do not talk price")),


    "is_performance_present": Noul(instructions="is the reivew talks about performance", criteria=NoulCriteria(true="if the review talks about the performance quality", false="if the review do not talk performance")),

    "main_category": Choice(instructions="review talks about which of the following category", criteria=choice_criteria),
    "camera_score": Score(instructions="Rate the camera score  based on the reivew", criteria=score_criteria),
    "battery_score": Score(instructions="Rate the battery score  based on the reivew", criteria=score_criteria),
    "price_score": Score(instructions="Rate the price score  based on the reivew", criteria=score_criteria),
    "performance_score": Score(instructions="Rate the performance score  based on the reivew", criteria=score_criteria),

}


" Approach 1  one by one  review b review "
state = {}
all_results = []
for i, doc in enumerate(reviews):
    state[f"review_{i+1}"] = doc
    response = jev_client.system_one(state=state,  questions=questions)

    all_results.append({
        "review": doc,
        "main_category": getattr(response.answers["main_category"], "score", )



    })

"Approach 2  entire all review in a single pass "
state = {}
all_results = []
for i, doc in enumerate(reviews):
    state[f"review_{i+1}"] = doc

response = jev_client.system_one(state=state,  questions=questions)


''''  get the result in the formo fo dictionary and make a pandas dataframe out of it '''
