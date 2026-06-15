# 🏭 Smart Factory - Sistema IoT para Monitoramento Industrial

Sistema distribuído baseado em microsserviços para monitoramento de máquinas industriais em tempo real utilizando MQTT, MongoDB, Redis, FastAPI e Azure.

---

# 📋 Visão Geral

O sistema simula sensores industriais enviando telemetria para um broker MQTT. Os dados são processados, autenticados por JWT, armazenados no MongoDB e disponibilizados em tempo real por meio de um dashboard web.

---

# Arquitetura

```text
Simulador
    │
    │ MQTT + TLS
    ▼
HiveMQ Cloud
    │
    ▼
Processador
    │
    │ JWT
    ▼
HiveMQ Cloud
    │
    ▼
Banco_Dados
    │
    ▼
TelemetriaSubject
 ├── MongoObserver
 └── RedisObserver
        │
        ▼
      Redis

API FastAPI
    │
    │ WebSocket (WSS)
    ▼
Dashboard Web
```

---

# 🔧 Tecnologias Utilizadas

## Backend

- Python 3.11
- FastAPI
- Paho MQTT
- PyMongo
- Redis
- PyJWT

## Infraestrutura

- Docker
- Docker Compose
- HiveMQ Cloud
- MongoDB Atlas
- Azure App Service

---

# Fluxo de Dados

## 1. Simulador

Gera dados de telemetria simulando sensores industriais:

- Temperatura
- Vibração
- Consumo de Energia

Publica mensagens MQTT no tópico:

```text
fabrica/raw
```

---

## 2. Processador

Consome mensagens do tópico:

```text
fabrica/raw
```

Aplica regras de negócio:

- Temperatura > 100°C
- Vibração > 5 mm/s
- Energia > 70 kW

Gera:

```json
{
  "status": "ALERTA",
  "alertas": [
    "energia_alta"
  ]
}
```

Assina a mensagem utilizando JWT e publica em:

```text
fabrica/processado
```

---

## 3. Banco_Dados

Consome mensagens processadas.

Valida o JWT antes de processar os dados.

Após a validação:

- Notifica os Observers
- Armazena no MongoDB
- Atualiza o cache Redis

---

## 4. API

Disponibiliza:

- Dashboard Web
- WebSocket em tempo real

Os dados são obtidos do Redis para reduzir a latência.

---

# 🐳 Execução Local

## Instalar o Docker

Antes de executar o projeto, instale:

* Docker
* Docker Compose

Verifique as instalações:

```bash
docker --version
docker compose version
```

## Clonar o repositório

```bash
git clone https://github.com/lucasngordon/smart-factory
cd smart-factory
```

## Configurar variáveis de ambiente

Copie:

```bash
cp .env.example .env
```

Em seguida, preencha as variáveis de ambiente de acordo com sua infraestrutura.

```env
# MQTT (HiveMQ Cloud)
MQTT_BROKER=xxxxxxxx.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=seu_usuario
MQTT_PASSWORD=sua_senha

# Tópicos MQTT
INPUT_TOPIC=fabrica/raw
OUTPUT_TOPIC=fabrica/processado

# MongoDB Atlas
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=sua_chave_secreta

# API
API_URL=https://smart-factory-api.azurewebsites.net
```

## Descrição das Variáveis

| Variável | Descrição |
|-----------|-----------|
| MQTT_BROKER | Endereço do broker MQTT |
| MQTT_PORT | Porta MQTT segura (TLS) |
| MQTT_USERNAME | Usuário do HiveMQ Cloud |
| MQTT_PASSWORD | Senha do HiveMQ Cloud |
| INPUT_TOPIC | Tópico de entrada da telemetria |
| OUTPUT_TOPIC | Tópico de saída da telemetria processada |
| MONGO_URI | String de conexão do MongoDB Atlas |
| REDIS_HOST | Host do Redis |
| REDIS_PORT | Porta do Redis |
| JWT_SECRET | Chave utilizada para assinatura dos tokens JWT |
| API_URL | URL pública da API |

> Observação: quando executado via Docker Compose, o valor de `REDIS_HOST` deve ser `redis`, pois esse é o nome do serviço definido no `docker-compose.yml`. Caso o Redis seja executado fora do Docker, utilize o endereço correspondente (por exemplo, `localhost`).

---

## Executando o Projeto

Após configurar o arquivo `.env`, execute:

```bash
docker compose up --build
```

### Verifique se os containers estão em execução

```bash
docker ps
```

Os seguintes serviços devem estar ativos:

```text
simulador
processador
banco_dados
redis
api
```

## Acessando o Dashboard

Após iniciar os containers:

```text
https://smart-factory-api-atcye9cbf0gtaad0.eastus-01.azurewebsites.net
```

caso esteja indisponível, hospede uma URL pública na Azure ou acesse o dashboard localmente:

```text
http://localhost:8000
```

O dashboard exibirá em tempo real:

* Temperatura
* Vibração
* Consumo de Energia
* Status

Os cartões mudam de cor quando valores críticos são detectados.

# Encerrando o Projeto

Parar todos os containers:

```bash
docker compose down
```

---

# ☁️ Deploy

Atualmente o deploy contempla:

| Serviço | Local |
|-----------|-----------|
| API FastAPI | Azure App Service |
| Dashboard | Azure App Service |
| MongoDB | MongoDB Atlas |
| MQTT Broker | HiveMQ Cloud |
| Redis | Docker Local |
| Simulador | Docker Local |
| Processador | Docker Local |
| Banco_Dados | Docker Local |

> Atualmente apenas a API e o Dashboard estão hospedados na Azure. Os serviços Simulador, Processador, Banco_Dados e Redis são executados localmente via Docker Compose durante o desenvolvimento.

---

# 🔒 Segurança

## MQTT com TLS

Todos os microsserviços utilizam:

```python
client.tls_set()
```

Comunicação segura pela porta:

```text
8883
```

---

## JWT

As mensagens processadas são assinadas digitalmente.

Fluxo:

```text
Processador
    │
    │ JWT
    ▼
Banco_Dados
```

Somente mensagens autenticadas são persistidas.

---

## HTTPS / WSS

A aplicação está hospedada no Azure App Service.

Protocolos utilizados:

```text
HTTPS
WSS (WebSocket Secure)
```

---

# 📁 Estrutura do Projeto

```text
src/
├── common/
│   ├── common.py
│   └── jwt_utils.py
│
├── observers/
│   ├── observer.py
│   ├── telemetria_subject.py
│   ├── mongo_observer.py
│   ├── redis_observer.py
│   └── circuit_breaker.py
│
├── api.py
├── simulador.py
├── processador.py
└── banco_dados.py

docker/
├── Dockerfile.api
├── Dockerfile.processador
├── Dockerfile.banco_dados
└── Dockerfile.simulador

.env
.gitignore
mosquitto.conf
docker-compose.yml
README.md
requirements.txt
```

---
