import os
from plato import Plato
from dotenv import load_dotenv
from apify_client import ApifyClient
from helpers import get_dict_structure, compare_dicts

load_dotenv(".env")
apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
plato = Plato(api_key=os.getenv("PLATO_API_KEY"), base_url=os.getenv("PLATO_BASE_URL"))

def run_apify_actor(actor_id: str, run_input: dict):
    run = apify_client.actor(actor_id).call(run_input=run_input)

    items = []
    
    for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    return items

def run_benchmark():
    session = plato.start_session()
    
    test_actor_id = "ZU6CrmA10PRnzY64J"
    test_url = "https://www.youtube.com/@destiny"
    test_input = {
        "start_urls": [
            {
                "url": test_url
            }
        ],
    }

    results = run_apify_actor(test_actor_id, test_input)[0]
    result_structure = get_dict_structure(results)

    task_prompt = f'''
    extract the details on this page in the following format: {result_structure}
    '''
    
    result = session.task(task=task_prompt, start_url=test_url)
    result_dict = result['data']['result']
    score = compare_dicts(results, result_dict)
    print(f"Score: {score}")

    session.end()

if __name__ == "__main__":
    run_benchmark()
