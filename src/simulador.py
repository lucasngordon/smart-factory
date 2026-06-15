import paho.mqtt.client as mqtt
import json
import time
import random
import os

BROKER = os.getenv("MQTT_BROKER")
PORT = int(os.getenv("MQTT_PORT", 8883))

TOPIC = os.getenv("TOPIC", "fabrica/raw")

MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

client = mqtt.Client(client_id="Sensor_MaquinaA")

# AUTH + TLS (HiveMQ Cloud)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()

while True:
    try:
        client.connect(BROKER, PORT, 60)
        break
    except Exception as e:
        print("Aguardando MQTT broker...", e)
        time.sleep(3)

client.loop_start()

print("Simulador iniciado...")

while True:
    payload = {
        "sensor_id": "maquinaA",
        "timestamp": int(time.time() * 1000),
        "temperatura": round(random.uniform(60, 110), 2),
        "vibracao": round(random.uniform(1, 6.5), 2),
        "energia": round(random.uniform(10, 80), 2)
    }

    payload["timestamp_envio"] = time.time_ns()
    client.publish(TOPIC, json.dumps(payload), qos=1)
    print("Enviado:", payload)

    time.sleep(2)