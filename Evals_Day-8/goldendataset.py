from openai import OpenAI
from deepeval import evaluate
import json
import os


def read_golden_datset(source_folder=None):
    queries = []
    expected_output_list = []
    if not source_folder:
        source_folder = "dataset"

    parent_of_cwd = os.path.dirname(__file__)
    target_folder = os.path.join(parent_of_cwd, source_folder)
    for file in os.listdir(target_folder):
        if os.path.isfile(os.path.join(target_folder, file)):
            file_path = os.path.join(target_folder, file)
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        # print(line)
                        clean_line = json.loads(line.strip())
                        user_query = clean_line.get("query", "")
                        expected_output = clean_line.get("expected_output", "")
                        queries.append(user_query)
                        expected_output_list.append(expected_output)
                        print(user_query)
            except (FileNotFoundError, Exception) as e:
                print(f" Error occured {e}")
    return queries, expected_output_list


read_golden_datset()
