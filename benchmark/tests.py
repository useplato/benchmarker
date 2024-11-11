class Test:
    def __init__(self, apify_client, plato_client):
        self.apify_client = apify_client
        self.plato_client = plato_client

    def run(self):
        raise NotImplementedError("Not implemented")

