import json
from common.circuit_breaker import CircuitBreaker
from .observer import Observer
import time

class RedisObserver(Observer):

    def __init__(self, redis_client):

        self.redis_client = redis_client

        self.breaker = CircuitBreaker(
            max_falhas=3,
            tempo_recuperacao=30
        )

    def update(self, payload):
        
        inicio = time.perf_counter()

        self.breaker.call(
            self.redis_client.set,
            "ultima_telemetria",
            json.dumps(payload)
        )
        
        fim = time.perf_counter()
        
        print(
            f"[Redis] {(fim - inicio) * 1000:.2f} ms"
        )