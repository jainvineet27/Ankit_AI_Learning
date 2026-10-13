import json
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import numpy as np

from typesafe_sdk import TypeSafeClient
from typesafe_sdk import Choice, Score, NoulCriteria, Noul

load_dotenv()

jev_client = TypeSafeClient()
client = OpenAI()

# 1. State definition
state = {
    "customer_message": "Shoes arrived two weeks late and in the wrong size. Also I see two charges of $120 on my card. What are you going to do about this?"
}

# 3. Score Criteria (Ordered rating levels)
severity_score_criteria = [
    "sev 1: Minor issue, single concern without financial impact",
    "sev 2: Moderate issue, single operational delay or wrong delivery",
    "sev 3: Critical issue, multiple compounding failures (delay + wrong item + double charge)"
]

# 4. Noul Criteria (Conditions / Rules for verification)
noul_urgency_criteria = NoulCriteria(
    true="Flag as true/urgent if financial discrepancies or duplicate charges exist",
    false="Flag as true/urgent if the shipment has exceeded expected delivery by over 7 days")

# 2. Criteria mappings
department_criteria = {
    "returns": "Exchanges, wrong or damaged items",
    "shipping": "Delivery status, delays, lost packages",
    "billing": "Charges, invoices, payment problems"
}

return_reason_criteria = {
    "wrong_size": "The item doesn't fit",
    "wrong_item": "A different product was delivered",
    "damaged": "The item arrived broken or faulty",
    "changed_mind": "The item is fine, the customer no longer wants it",
    "other": "A return reason that fits none of the above"
}

shipping_issue_criteria = {
    "not_delivered": "The package never arrived",
    "delayed": "The package is late but still on its way",
    "wrong_address": "The package went to the wrong place",
    "damaged_in_transit": "The package arrived damaged",
    "other": "A shipping problem that fits none of the above"
}

requested_resolution_criteria = {
    "exchange": "Swap the item for a different one",
    "refund": "Money back",
    "replacement": "The same item sent again",
    "information": "Just an answer, no action needed"
}

tone_criteria = {
    "calm": "Calm and composed tone",
    "frustrated": "Annoyed or dissatisfied with the service",
    "angry": "Aggressive, highly upset, or hostile tone"
}

# 3. Questions configuration using Choice
questions = {
    # Score type
    "ticket_severity": Score(
        instructions="Evaluate ticket severity based on the cumulative customer impact",
        score_criteria=severity_score_criteria
    ),

    # Noul type with criteria
    "is_immediate_escalation_required": Noul(
        instructions="Determine if this ticket requires immediate manager escalation",
        criteria=noul_urgency_criteria
    ),

    "department": Choice(
        instructions="Which team should handle this?",
        choice_criteria=department_criteria
    ),
    "return_reason": Choice(
        instructions="If the customer wants to return something, why?",
        choice_criteria=return_reason_criteria
    ),
    "shipping_issue": Choice(
        instructions="If this is a shipping problem, which kind is it?",
        choice_criteria=shipping_issue_criteria
    ),
    "requested_resolution": Choice(
        instructions="What does the customer want to happen?",
        choice_criteria=requested_resolution_criteria
    ),
    "tone": Choice(
        instructions="What is the customer's tone?",
        choice_criteria=tone_criteria
    )
}

# 4. Execution & Output
response = jev_client.system_one(state=state, questions=questions)

for k, v in response.answers.items():
    print(k, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", v)
