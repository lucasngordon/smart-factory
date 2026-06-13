# Smart Factory - Arquitetura de Microserviços com MQTT

## Descrição

Este projeto simula um ambiente industrial utilizando arquitetura de microserviços, comunicação assíncrona via MQTT e armazenamento de dados em MongoDB.

O sistema gera dados de sensores industriais, processa regras de negócio, armazena os dados processados e os disponibiliza em um dashboard web em tempo real.

# Pré-requisitos

Antes de executar o projeto, instale:

* Docker
* Docker Compose

Verifique as instalações:

```bash
docker --version
docker compose version
```

---

# Configuração

## 1. Clonar o repositório

```bash
git clone https://github.com/lucasngordon/smart-factory
cd smart-factory
```

---

## 2. Configurar variável de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo .env:

MongoDB
MONGO_URI=sua_string_de_conexao_mongodb

MQTT Broker
MQTT_BROKER=mosquitto
MQTT_PORT=1883

MQTT Topic base
TOPIC=fabrica/linha1/maquinaA/metricas

# Executando o Projeto

Na raiz do projeto:

```bash
docker compose up --build
```

O Docker irá:

* Criar o broker MQTT
* Criar o simulador
* Criar o processador
* Criar o serviço de persistência
* Criar a API FastAPI

---

## Executar em segundo plano

```bash
docker compose up -d --build
```

---

## Verificar containers em execução

```bash
docker ps
```

Containers esperados:

```text
mosquitto
simulador
processador
banco_dados
api
```

---
# Acessando o Dashboard

Após iniciar os containers:

```text
http://localhost:8000
```

O dashboard exibirá em tempo real:

* Temperatura
* Vibração
* Consumo de Energia
* Status

Os cartões mudam de cor quando valores críticos são detectados.

---


# Encerrando o Projeto

Parar todos os containers:

```bash
docker compose down
```

---

# Tecnologias Utilizadas

* Python 3
* FastAPI
* MQTT
* Eclipse Mosquitto
* MongoDB
* Docker
* Docker Compose
* WebSocket

---
