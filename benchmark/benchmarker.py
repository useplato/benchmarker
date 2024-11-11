import os
from plato import Plato
from dotenv import load_dotenv

load_dotenv(".env")

plato = Plato(api_key=os.getenv("PLATO_API_KEY"), base_url=os.getenv("PLATO_BASE_URL"))

def run_benchmark():
    session = plato.start_session()
    session.end()

if __name__ == "__main__":
    run_benchmark()
