import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import os
import time
import redis
from observers.telemetria_subject import TelemetriaSubject
from observers.mongo_observer import MongoObserver
from observers.redis_observer import RedisObserver

BROKER = os.getenv("MQTT_BROKER")
PORT = int(os.getenv("MQTT_PORT", 8883))

TOPIC = os.getenv("OUTPUT_TOPIC", "fabrica/processado")

MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

MONGO_URI = os.getenv("MONGO_URI")

client_mongo = MongoClient(MONGO_URI)
db = client_mongo["smart_factory"]
col = db["telemetria"]

def on_connect(client, userdata, flags, rc):
    print("CONN CODE:", rc)

    if rc == 0:
        print("Mongo Writer conectado")
        client.subscribe(TOPIC)
    else:
        print("Erro MQTT connect")
        
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

subject = TelemetriaSubject()

subject.add_observer(
    MongoObserver(col)
)

subject.add_observer(
    RedisObserver(redis_client)
)


def on_message(client, userdata, msg):
    try:

        payload = json.loads(msg.payload.decode())

        payload["timestamp"] = int(time.time() * 1000)

        subject.notify(payload)
        
        print("Salvo no MongoDB")

    except Exception as e:

        print("Erro:", e)


client = mqtt.Client(client_id="MongoWriter")

client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()