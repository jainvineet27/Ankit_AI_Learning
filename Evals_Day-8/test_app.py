from deepeval import evaluate
from deepeval.test_case import LLMTestCase, SingleTurnParams
from deepeval.metrics import GEval

from dotenv import load_dotenv

load_dotenv()
# custom test case ...
correctness_metric = GEval(
    name="Correctness",
    criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
    evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT,
                       SingleTurnParams.EXPECTED_OUTPUT],
    threshold=0.5
)

test_case_list = LLMTestCase(
    input="I have a persistent cough and fever. Should I be worried?",
    # Replace this with the actual output from your LLM application
    actual_output="A persistent cough and fever could signal various illnesses, from minor infections to more serious conditions like pneumonia or COVID-19. It's advisable to seek medical attention if symptoms worsen, persist beyond a few days, or if you experience difficulty breathing, chest pain, or other concerning signs.",
    expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral infection to more serious conditions like pneumonia or COVID-19. You should seek medical attention if your symptoms worsen, persist for more than a few days, or are accompanied by difficulty breathing, chest pain, or other concerning signs."
    # retrieved_context = ['']
)

result = evaluate(test_cases=test_case_list, metric=[correctness_metric])
print(result.test_results)


'''
GOlden   data sert in jsonl 
question ,  expected output ....    

now  read this file and make 4 parameters 
question 
expected_output 
actual_output  
retrieved_context =  

Now supply this to  testcase object 

Context Recall 
precision == reranking and  retried chunks / total of chunks obtained 
Answer relevancy  ... question  and actual output .. 

'''
