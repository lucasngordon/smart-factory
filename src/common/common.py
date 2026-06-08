import os

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = os.getenv("TOPIC", "fabrica/linha1/maquinaA/metricas")
MONGO_URI = os.getenv("MONGO_URI")