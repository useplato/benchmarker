import argparse
import datetime
import json
import os
import time

from apify_client import ApifyClient
from benchmark_viewer.viewer import BenchmarkViewer
from dotenv import load_dotenv
from helpers.apify_helpers import run_apify_actor
from helpers.general_helpers import compare_dicts, get_dict_structure
from plato import Plato

load_dotenv(".env")


def run_apify_test_case(test_cases, test_case, apify_client):
    print("running apify actor...")
    start_time = time.time()
    apify_results = run_apify_actor(
        test_case["id"], test_case["example_input"], apify_client
    )[0]
    end_time = time.time()
    apify_time = end_time - start_time
    print(f"Apify actor finished in {apify_time} seconds")
    test_case["apify_time"] = apify_time

    test_case["apify_results"] = apify_results
    with open("test_data/test_cases.json", "w") as f:
        json.dump(test_cases, f, indent=4)

    return test_case


def run_plato_test_case(test_case, plato_client):
    apify_results = test_case["apify_results"]
    result_model = get_dict_structure(apify_results)

    plato_task_prompt = test_case["plato_task_prompt"]["message"]
    plato_start_url = test_case["plato_task_prompt"]["start_url"]
    print("running plato...")
    start_time = time.time()
    result = plato_client.task(
        task=plato_task_prompt,
        start_url=plato_start_url,
        response_format=result_model,
    )
    end_time = time.time()
    plato_time = end_time - start_time
    print(f"Plato finished in {plato_time} seconds")

    result_dict = result["data"]["result"]

    return result_dict, plato_time


def run_benchmark(rerun_apify=False):
    apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
    plato = Plato(
        api_key=os.getenv("PLATO_API_KEY"), base_url=os.getenv("PLATO_BASE_URL")
    )
    session = plato.start_session()
    results = []

    with open("test_data/test_cases.json", "r") as f:
        test_cases = json.load(f)

    for test_case in test_cases:
        try:
            print(f"Running test case: {test_case['name']}")

            if (not rerun_apify) and ("apify_results" in test_case):
                print("using cached apify results")
            else:
                test_case = run_apify_test_case(test_cases, test_case, apify_client)

            plato_results, plato_time = run_plato_test_case(test_case, session)

            apify_results = test_case["apify_results"]
            apify_time = test_case["apify_time"]
            score = compare_dicts(apify_results, plato_results)
            time_diff = plato_time - apify_time
            print(f"Score: {score}, Time diff: {time_diff}")

            test_results = {
                "name": test_case["name"],
                "completed": True,
                "apify_results": apify_results,
                "plato_results": plato_results,
                "apify_time": apify_time,
                "plato_time": plato_time,
                "score": score,
                "time_diff": time_diff,
            }
            results.append(test_results)
        except Exception as e:
            print(f"Error: {e}")
            results.append(
                {
                    "name": test_case["name"],
                    "completed": False,
                    "error": str(e),
                }
            )

    session.end()

    benchmark_file_name = f"benchmark_results_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    with open(f"test_data/{benchmark_file_name}", "w") as f:
        json.dump(results, f, indent=4)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the benchmark.")
    parser.add_argument(
        "-r", "--rerunapify", action="store_true", help="Rerun the apify actor"
    )
    args = parser.parse_args()
    results = run_benchmark(args.rerunapify)
    viewer = BenchmarkViewer(results)
    viewer.mainloop()
