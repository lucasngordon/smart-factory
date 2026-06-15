import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import os
import time
import redis

from observers.telemetria_subject import TelemetriaSubject
from observers.mongo_observer import MongoObserver
from observers.redis_observer import RedisObserver
from common.jwt_utils import validar_token

# =========================
# CONFIGURAÇÕES
# =========================

BROKER = os.getenv("MQTT_BROKER")
PORT = int(os.getenv("MQTT_PORT", 8883))

TOPIC = os.getenv("OUTPUT_TOPIC", "fabrica/processado")

MQTT_USER = os.getenv("MQTT_USERNAME")
MQTT_PASS = os.getenv("MQTT_PASSWORD")

MONGO_URI = os.getenv("MONGO_URI")

print("JWT_SECRET carregado:", bool(os.getenv("JWT_SECRET")))

# =========================
# MONGODB
# =========================

client_mongo = MongoClient(MONGO_URI)

db = client_mongo["smart_factory"]
col = db["telemetria"]

# =========================
# REDIS
# =========================

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# =========================
# OBSERVER
# =========================

subject = TelemetriaSubject()

subject.add_observer(
    MongoObserver(col)
)

subject.add_observer(
    RedisObserver(redis_client)
)

# =========================
# MQTT CALLBACKS
# =========================

def on_connect(client, userdata, flags, rc):

    print("CONN CODE:", rc)

    if rc == 0:

        print("Mongo Writer conectado")

        client.subscribe(TOPIC)

        print(f"Inscrito no tópico: {TOPIC}")

    else:

        print("Erro ao conectar ao MQTT")


def on_message(client, userdata, msg):

    try:

        mensagem = json.loads(
            msg.payload.decode()
        )

        # ---------------------
        # Validação JWT
        # ---------------------

        token = mensagem.get("token")

        if not token:

            print("Mensagem sem JWT")
            return

        dados_token = validar_token(token)

        if not dados_token:

            print("JWT inválido")
            return

        print(
            f"Mensagem autenticada por: {dados_token.get('service')}"
        )

        # ---------------------
        # Payload
        # ---------------------

        payload = mensagem.get("dados")

        if not payload:

            print("Payload inválido")
            return

        payload["timestamp"] = int(
            time.time() * 1000
        )

        # ---------------------
        # Observer Pattern
        # ---------------------

        subject.notify(payload)

        print(
            f"Telemetria processada: "
            f"{payload.get('sensor_id', 'desconhecido')}"
        )

    except json.JSONDecodeError:

        print("JSON inválido recebido")

    except Exception as e:

        print("Erro:", e)


# =========================
# MQTT CLIENT
# =========================

client = mqtt.Client(
    client_id="MongoWriter"
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