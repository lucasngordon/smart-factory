import json
from .observer import Observer

class RedisObserver(Observer):

    def __init__(self, redis_client):
        self.redis_client = redis_client

    def update(self, payload):

        self.redis_client.set(
            "ultima_telemetria",
            json.dumps(payload)
        )

        print("[Redis] Cache atualizado")