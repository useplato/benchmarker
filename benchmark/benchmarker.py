import os
from plato import Plato
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv(".env")

apify_client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

plato = Plato(api_key=os.getenv("PLATO_API_KEY"), base_url=os.getenv("PLATO_BASE_URL"))

def run_benchmark():
    session = plato.start_session()

    session.end()

if __name__ == "__main__":
    run_benchmark()
