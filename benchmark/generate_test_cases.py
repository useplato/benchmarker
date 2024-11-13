import argparse
import json
import os

from helpers.apify_helpers import get_actors_from_store, get_example_actor_input
from helpers.general_helpers import limit_array_values
from helpers.openai_helpers import generate_task_prompt
from openai import OpenAI


def generate_test_cases(number_of_tests: int = 10):
    openai_client = OpenAI()

    test_cases = []
    actors = []
    iterations = 0
    while len(actors) < number_of_tests:
        fetched_actors = get_actors_from_store(
            os.getenv("APIFY_API_TOKEN"),
            limit=number_of_tests,
            offset=iterations * number_of_tests,
        )
        filtered_actors = [
            actor
            for actor in fetched_actors["data"]["items"]
            if actor.get("notice", "") != "UNDER_MAINTENANCE"
        ]
        actors.extend(filtered_actors)
        actors = actors[:number_of_tests]
        iterations += 1

    for actor in actors:
        example_input = get_example_actor_input(
            os.getenv("APIFY_API_TOKEN"), actor["id"]
        )
        example_input_limited = limit_array_values(example_input)
        cur_actor_details = {
            "id": actor["id"],
            "name": actor["name"],
            "username": actor["username"],
            "description": actor["description"],
            "example_input": example_input_limited,
        }
        task_prompt = generate_task_prompt(cur_actor_details, openai_client)
        cur_actor_details["plato_task_prompt"] = task_prompt
        test_cases.append(cur_actor_details)

    with open("test_data/test_cases.json", "w") as f:
        json.dump(test_cases, f, indent=4)

    print(f"Generated {len(test_cases)} test cases.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test cases for actors.")
    parser.add_argument(
        "-n", "--number", type=int, default=10, help="Number of test cases to generate"
    )
    args = parser.parse_args()
    generate_test_cases(args.number)
