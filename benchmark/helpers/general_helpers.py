import json
import re
from typing import Any, List

import requests
from bs4 import BeautifulSoup
from deepdiff import DeepDiff
from pydantic import BaseModel, create_model


def get_dict_structure(d: Any) -> BaseModel:
    if isinstance(d, dict):
        fields = {k: (get_dict_structure(v), ...) for k, v in d.items()}
        return create_model("DynamicModel", **fields)
    elif isinstance(d, list):
        if d:
            return List[get_dict_structure(d[0])]
        else:
            return List[Any]
    else:
        return type(d)


def count_nested_keys(d, parent_key=""):
    count = 0
    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        count += 1
        if isinstance(value, dict):
            count += count_nested_keys(value, full_key)
    return count


def compare_dicts(source_dict, target_dict):
    diff = DeepDiff(source_dict, target_dict, ignore_order=True)

    total_diff_count = len(diff.get("values_changed", {})) + len(
        diff.get("dictionary_item_removed", {})
    )

    total_keys_in_source = count_nested_keys(source_dict)

    # Avoid division by zero
    if total_keys_in_source == 0:
        return 100.0 if source_dict == target_dict else 0.0

    similarity_score = (
        (total_keys_in_source - total_diff_count) / total_keys_in_source
    ) * 100
    return max(0, similarity_score)


def extract_run_input_from_apify_url(url: str):
    response = requests.get(url)
    page_content = response.text
    soup = BeautifulSoup(page_content, "html.parser")

    code_blocks = soup.find_all("code")
    run_input_lines = []

    for block in code_blocks:
        reading_input = False
        for line in block.text.split("\n"):
            formatted_line = re.sub(r"^\d+\s*", "", line.strip())
            if (formatted_line.strip() == "") and reading_input:
                break
            if "run_input = {" in formatted_line:
                reading_input = True
            if reading_input:
                run_input_lines.append(formatted_line)

    if run_input_lines:
        run_input_lines[0] = run_input_lines[0].replace("run_input = ", "", 1)
    run_input_str = "".join(run_input_lines)
    try:
        # Use regex to replace single quotes with double quotes
        run_input_str = re.sub(r"'", '"', run_input_str)

        # Remove trailing commas
        run_input_str = re.sub(r",\s*([}\]])", r"\1", run_input_str)

        # Replace Python boolean with JSON boolean
        run_input_str = re.sub(r"\bTrue\b", "true", run_input_str)
        run_input_str = re.sub(r"\bFalse\b", "false", run_input_str)

        run_input_str = run_input_str.strip()

        example_input = json.loads(run_input_str)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        example_input = {}

    return example_input


def limit_array_values(input_dict):
    if isinstance(input_dict, dict):
        for key, value in input_dict.items():
            if isinstance(value, list) and len(value) > 1:
                input_dict[key] = value[:1]
            elif isinstance(value, dict):
                input_dict[key] = limit_array_values(value)
    return input_dict
