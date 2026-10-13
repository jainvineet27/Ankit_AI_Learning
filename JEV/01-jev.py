from typesafe_sdk import TypeSafeClient
from typesafe_sdk import Noul, NoulCriteria, Choice, Score
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


jev_client = TypeSafeClient()
client = OpenAI()
choice_criteria = {"finance": "deal with payments, finance, pricing and refunds",
                   "marketing": "deal with email messages or sms  ",
                   "orders": "deals with order realted queries",
                   }

score_criteria = ["dissatisfied: quite angry, agitated",
                  "neutral : he i ok / normal", "satisfied : he is miling and cheerful"]


user_query = " I have been charged twice for my product purchase, can you please help me in refund"

state = user_query
questions = {
    "is_it_urgent": Noul(instructions="based onthe user question determine whether this needs to be fxxied on priority basis"),
    "which_team": Choice(instructions="based on the user question which team should act on this", criteria=choice_criteria),
    "mood_of_user": Score(instructions="based onthe user input determine mood of the user", criteria=score_criteria)

}

response = jev_client.system_one(state=state, questions=questions)
print(response.answers)
print("--------------------------------------------------------------")

for key, value in response.answers.item():
    print(key, ">>>>>>>>>>>>>>>>>>>>", value)
