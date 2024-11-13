import requests
from apify_client import ApifyClient
from helpers.general_helpers import extract_run_input_from_apify_url


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


def get_example_actor_input(api_key: str, actor_id: str):
    actor_info = get_actor(api_key, actor_id)
    author_username = actor_info["data"]["username"]
    actor_name = actor_info["data"]["name"]

    url = f"https://apify.com/{author_username}/{actor_name}/api/python"
    example_input = extract_run_input_from_apify_url(url)
    return example_input


def run_apify_actor(actor_id: str, run_input: dict, apify_client: ApifyClient):
    run = apify_client.actor(actor_id).call(run_input=run_input)

    items = []

    for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    return items
