import paho.mqtt.client as mqtt
import json
import os
from src.common.jwt_utils import gerar_token

# =========================
# CONFIGURAÇÕES
# =========================

BROKER = os.getenv("MQTT_BROKER")
PORT = int(os.getenv("MQTT_PORT", 8883))

INPUT_TOPIC = os.getenv("INPUT_TOPIC", "fabrica/raw")
OUTPUT_TOPIC = os.getenv("OUTPUT_TOPIC", "fabrica/processado")

MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

print("JWT_SECRET carregado:", bool(os.getenv("JWT_SECRET")))

# =========================
# MQTT CALLBACKS
# =========================

def on_connect(client, userdata, flags, rc):

    print("CONN CODE:", rc)

    if rc == 0:

        print("Processador conectado")

        client.subscribe(INPUT_TOPIC)

        print(f"Inscrito no tópico: {INPUT_TOPIC}")

    else:

        print("Erro conexão MQTT")


def on_message(client, userdata, msg):

    try:
        
        payload = json.loads(
            msg.payload.decode()
        )

        temperatura = float(
            payload.get("temperatura", 0)
        )

        vibracao = float(
            payload.get("vibracao", 0)
        )

        energia = float(
            payload.get("energia", 0)
        )

        alertas = []

        if temperatura > 100:
            alertas.append(
                "temperatura_critica"
            )

        if vibracao > 5:
            alertas.append(
                "vibracao_alta"
            )

        if energia > 70:
            alertas.append(
                "energia_alta"
            )

        payload["alertas"] = alertas

        payload["status"] = (
            "ALERTA"
            if alertas
            else "NORMAL"
        )

        token = gerar_token()

        mensagem = {
            "token": token,
            "dados": payload
        }

        client.publish(
            OUTPUT_TOPIC,
            json.dumps(mensagem)
        )

        print(
            f"Processado: "
            f"{payload.get('sensor_id', 'desconhecido')}"
        )
        
    except json.JSONDecodeError:

        print("JSON inválido recebido")

    except Exception as e:

        print(
            f"Erro ao processar mensagem: {e}"
        )


# =========================
# MQTT CLIENT
# =========================

client = mqtt.Client(
    client_id="Processador"
)

client.username_pw_set(
    MQTT_USER,
    MQTT_PASS
)

client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

print("Conectando ao broker MQTT...")

client.connect(
    BROKER,
    PORT,
    60
)

client.loop_forever()