import paho.mqtt.client as mqtt
import json
import time
import random
import os

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = os.getenv("TOPIC", "fabrica/linha1/maquinaA/metricas")

client = mqtt.Client(client_id="Sensor_MaquinaA")


# conexão com retry
while True:
    try:
        client.connect(BROKER, PORT, 60)
        break
    except Exception as e:
        print("Aguardando MQTT broker...", e)
        time.sleep(3)

client.loop_start()

print("Simulador iniciado...")

try:
    while True:
        payload = {
            "sensor_id": "maquinaA",
            "timestamp": int(time.time() * 1000),
            "temperatura": round(random.uniform(60, 110), 2),
            "vibracao": round(random.uniform(1, 6.5), 2)
        }

        client.publish(TOPIC, json.dumps(payload), qos=1)

        print(f"Temp={payload['temperatura']} | Vib={payload['vibracao']}")
        print("RECEBI:", payload)
        time.sleep(2)

except KeyboardInterrupt:
    print("Encerrando simulador...")
    client.loop_stop()
    client.disconnect()