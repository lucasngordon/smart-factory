import paho.mqtt.client as mqtt
import json
import time
import os

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))

INPUT_TOPIC = os.getenv("INPUT_TOPIC", "fabrica/raw")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "fabrica/processado")


def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("Processador conectado")
        client.subscribe(INPUT_TOPIC, qos=1)
    else:
        print("Erro MQTT:", rc)


def on_message(client, userdata, msg):

    try:

        payload = json.loads(msg.payload.decode())

        temperatura = float(payload.get("temperatura", 0))
        vibracao = float(payload.get("vibracao", 0))
        energia = float(payload.get("energia", 0))

        alertas = []

        if temperatura > 100:
            alertas.append("temperatura_critica")

        if vibracao > 5:
            alertas.append("vibracao_alta")

        if energia > 70:
            alertas.append("energia_alta")

        payload["alertas"] = alertas

        payload["status"] = (
            "ALERTA"
            if alertas
            else "NORMAL"
        )

        client.publish(
            OUTPUT_TOPIC,
            json.dumps(payload),
            qos=1
        )

        print("Processado:", payload)

    except Exception as e:
        print("Erro:", e)


client = mqtt.Client(client_id="Processador")

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