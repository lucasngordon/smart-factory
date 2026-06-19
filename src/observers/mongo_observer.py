from common.circuit_breaker import CircuitBreaker
from .observer import Observer
import time

class MongoObserver(Observer):

    def __init__(self, collection):

        self.collection = collection

        self.breaker = CircuitBreaker(
            max_falhas=3,
            tempo_recuperacao=30
        )

    def update(self, payload):
        
        inicio = time.perf_counter()

        self.breaker.call(
            self.collection.insert_one,
            payload
        )
        
        fim = time.perf_counter()
        
        print(
            f"[Mongo] {(fim - inicio) * 1000:.2f} ms"
        )