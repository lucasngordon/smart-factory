from .observer import Observer

class MongoObserver(Observer):

    def __init__(self, collection):
        self.collection = collection

    def update(self, payload):

        result = self.collection.insert_one(payload)

        print(
            f"[MongoDB] Salvo: {result.inserted_id}"
        )