from common.circuit_breaker import CircuitBreaker
from .observer import Observer

class MongoObserver(Observer):

    def __init__(self, collection):

        self.collection = collection

        self.breaker = CircuitBreaker(
            max_falhas=3,
            tempo_recuperacao=30
        )

    def update(self, payload):

        self.breaker.call(
            self.collection.insert_one,
            payload
        )