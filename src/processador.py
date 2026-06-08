import paho.mqtt.client as mqtt
import json
import time
import os

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = os.getenv("TOPIC", "fabrica/linha1/maquinaA/metricas")

# -------------------------
# CALLBACK: conexão
# -------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("🟢 Conectado ao MQTT com sucesso")
        client.subscribe(TOPIC, qos=1)
        print(f"📡 Subscrito no tópico: {TOPIC}")
    else:
        print(f"🔴 Falha na conexão MQTT. Código: {rc}")

# -------------------------
# CALLBACK: mensagens
# -------------------------
def on_message(client, userdata, msg):
    try:
        print("\n📩 Mensagem recebida!")
        print(f"Tópico: {msg.topic}")

        payload = json.loads(msg.payload.decode())
        print("Payload:", payload)

        temp = float(payload.get("temperatura", 0))
        vib = float(payload.get("vibracao", 0))

        if temp > 100:
            print(f"⚠️ ALERTA: temperatura crítica {temp}°C")

        if vib > 5:
            print(f"⚠️ ALERTA: vibração alta {vib}")

    except json.JSONDecodeError:
        print("❌ Erro: JSON inválido")
    except Exception as e:
        print("❌ Erro no processamento:", e)

# -------------------------
# CLIENTE MQTT
# -------------------------
client = mqtt.Client(client_id="Processador")

client.on_connect = on_connect
client.on_message = on_message

# -------------------------
# CONEXÃO COM RETRY
# -------------------------
while True:
    try:
        print("🔄 Conectando ao MQTT...")
        client.connect(BROKER, PORT, 60)
        break
    except Exception as e:
        print("⏳ Aguardando MQTT broker...", e)
        time.sleep(3)

client.loop_forever()