import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import os
import time

URI = os.getenv("MONGO_URI")
BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = os.getenv("TOPIC", "fabrica/linha1/maquinaA/metricas")

if not URI:
    raise ValueError("MONGO_URI não definida")

# Mongo connect retry
while True:
    try:
        mongo = MongoClient(URI, serverSelectionTimeoutMS=5000)
        mongo.server_info()
        print("Mongo conectado")
        break
    except Exception as e:
        print("Tentando Mongo...", e)
        time.sleep(3)

db = mongo["smart_factory"]
col = db["telemetria"]

def on_connect(client, userdata, flags, rc):
    print("MQTT conectado (mongo writer)")
    client.subscribe(TOPIC, qos=1)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        ts = payload.get("timestamp")
        payload["timestamp"] = (
            datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            if ts else datetime.now(timezone.utc)
        )

        payload["sensor_id"] = payload.get("sensor_id", "maquinaA")

        col.insert_one(payload)

    except Exception as e:
        print("Erro Mongo writer:", e)

client = mqtt.Client(client_id="MongoWriter")

client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        client.connect(BROKER, PORT, 60)
        break
    except Exception as e:
        print("Aguardando MQTT...", e)
        time.sleep(3)

client.loop_forever()