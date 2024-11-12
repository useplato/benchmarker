import requests
from helpers.general_helpers import extract_run_input_from_page


def get_actors_from_store(
    api_key: str,
    limit: int = 10,
    offset: int = 0,
    search: str = "",
    sort_by: str = "popularity",
    category: str = "SOCIAL_MEDIA",
    username: str = "",
    pricing_model: str = "FREE",
):
    query_params = {
        "limit": limit,
        "offset": offset,
        "search": search,
        "sortBy": sort_by,
        "category": category,
        "username": username,
        "pricingModel": pricing_model,
    }
    query_params = {k: v for k, v in query_params.items() if v != ""}
    url = f"https://api.apify.com/v2/store?token={api_key}"
    response = requests.get(url, params=query_params)
    return response.json()


def get_actor(api_key: str, actor_id: str):
    url = f"https://api.apify.com/v2/acts/{actor_id}?token={api_key}"
    response = requests.get(url)
    return response.json()


def get_actor_input_schema(api_key: str, actor_id: str):
    url = f"https://api.apify.com/v2/acts/{actor_id}/input-schema?token={api_key}"
    response = requests.get(url)
    return response.json()


def run_example_actor_task(api_key: str, actor_id: str):
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={api_key}"
    response = requests.get(url)
    return response.json()


def get_example_actor_input(api_key: str, actor_id: str):
    actor_info = get_actor(api_key, actor_id)
    author_username = actor_info["data"]["username"]
    actor_name = actor_info["data"]["name"]

    url = f"https://apify.com/{author_username}/{actor_name}/api/python"
    response = requests.get(url)
    example_input = extract_run_input_from_page(response.text)
    print(url)
    return example_input
