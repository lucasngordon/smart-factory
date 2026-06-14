import json
from common.circuit_breaker import CircuitBreaker
from .observer import Observer

class RedisObserver(Observer):

    def __init__(self, redis_client):

        self.redis_client = redis_client

        self.breaker = CircuitBreaker(
            max_falhas=3,
            tempo_recuperacao=30
        )

    def update(self, payload):

        self.breaker.call(
            self.redis_client.set,
            "ultima_telemetria",
            json.dumps(payload)
        )