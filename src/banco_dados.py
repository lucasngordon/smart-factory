import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import os
import time

# MQTT (HiveMQ Cloud)
BROKER = os.getenv("MQTT_BROKER")
PORT = int(os.getenv("MQTT_PORT", 8883))

TOPIC = os.getenv("OUTPUT_TOPIC", "fabrica/processado")

MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI não definida")

client_mongo = MongoClient(MONGO_URI)
db = client_mongo["smart_factory"]
col = db["telemetria"]

def on_connect(client, userdata, flags, rc):
    print("Mongo Writer conectado")
    client.subscribe(TOPIC, qos=1)

def on_message(client, userdata, msg):

    try:
        payload = json.loads(msg.payload.decode())

        # 🔥 PADRONIZA TIMESTAMP (OBRIGATÓRIO)
        payload["timestamp"] = int(time.time() * 1000)

        col.insert_one(payload)

        print("SALVANDO NO MONGO:", payload)

    except Exception as e:
        print("Erro Mongo:", e)

client = mqtt.Client(client_id="MongoWriter")

client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()

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