from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common.jwt_utils import gerar_token, validar_token
from pymongo import MongoClient
import os
import asyncio
import redis
import json

# -------------------------
# ENV CONFIG
# -------------------------
MONGO_URI = os.getenv("MONGO_URI")
API_URL = os.getenv("API_URL", "http://localhost:8000")

if not MONGO_URI:
    raise ValueError("MONGO_URI não configurada")

# -------------------------
# MONGO
# -------------------------
client = MongoClient(MONGO_URI)
db = client["smart_factory"]
col = db["telemetria"]

# -------------------------
# FASTAPI
# -------------------------
app = FastAPI()

security = HTTPBearer()
# -------------------------
# REDIS
# -------------------------
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

#Função de validação

def autenticar(
    credenciais: HTTPAuthorizationCredentials = Depends(security)
):

    payload = validar_token(
        credenciais.credentials
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    return payload

# -------------------------
# DASHBOARD
# -------------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>Smart Factory Dashboard</title>

        <style>
            body {
                font-family: Arial;
                background-color: #0f172a;
                color: white;
                text-align: center;
            }

            .container {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }

            .card {
                background: #1e293b;
                padding: 20px;
                border-radius: 15px;
                width: 220px;
            }

            .alerta {
                background: #7f1d1d;
                border: 2px solid #ef4444;
                box-shadow: 0 0 20px #ef4444;
                animation: piscar 1s infinite;
            }

            @keyframes piscar {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }

            .temp {
                color: #f87171;
                font-size: 32px;
            }

            .vib {
                color: #60a5fa;
                font-size: 32px;
            }

            .eng {
                color: #34d399;
                font-size: 32px;
            }

            .sts {
                color: white;
                font-size: 28px;
            }
        </style>
    </head>

    <body>

        <h1>🏭 Smart Factory Dashboard</h1>

        <div class="container">
            <div class="card">
                <h2>Temperatura</h2>
                <div id="tempCard" class="temp">--</div>
            </div>

            <div class="card">
                <h2>Vibração</h2>
                <div id="vibCard" class="vib">--</div>
            </div>

            <div class="card">
                <h2>Energia</h2>
                <div id="engCard" class="eng">--</div>
            </div>

            <div class="card">
                <h2>Status</h2>
                <div id="statusCard" class="sts">--</div>
            </div>
        </div>

        <script>
            async function iniciarDashboard() {
                try {

                    const resposta = await fetch("/login", {
                        method: "POST"
                    });

                    const auth = await resposta.json();

                    const token = auth.token;

                    const ws = new WebSocket(
                        (location.protocol === "https:" ? "wss://" : "ws://") +
                        location.host +
                        "/ws?token=" + token
                    );

                    ws.onmessage = function(event) {

                        const data = JSON.parse(event.data);

                        const temp = Number(data.temperatura);
                        const vib = Number(data.vibracao);
                        const eng = Number(data.energia);

                        document.getElementById("tempCard").innerText =
                            temp.toFixed(1) + " °C";

                        document.getElementById("vibCard").innerText =
                            vib.toFixed(2) + " mm/s";

                        document.getElementById("engCard").innerText =
                            eng.toFixed(2) + " kW";

                        document.getElementById("statusCard").innerText =
                            data.status || "N/A";

                        document.getElementById("tempCard")
                            .classList.toggle("alerta", temp > 100);

                        document.getElementById("vibCard")
                            .classList.toggle("alerta", vib > 5);

                        document.getElementById("engCard")
                            .classList.toggle("alerta", eng > 70);
                    };

                    ws.onclose = function() {
                        console.log("WebSocket encerrado");
                    };

                } catch (erro) {

                    console.error(
                        "Erro ao autenticar:",
                        erro
                    );
                }
            }

            iniciarDashboard();
        </script>
    </body>
    </html>
    """

# -------------------------
# WEBSOCKET
# -------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    payload = validar_token(token)

    if not payload:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()

    try:
        while True:

            dado = col.find_one(
                sort=[("timestamp", -1)]
            )

            if dado:

                await websocket.send_json({
                    "temperatura": float(dado.get("temperatura", 0)),
                    "vibracao": float(dado.get("vibracao", 0)),
                    "energia": float(dado.get("energia", 0)),
                    "status": dado.get("status"),
                    "alertas": dado.get("alertas", [])
                })

            await asyncio.sleep(2)

    except Exception as e:
        print("ERRO WS:", e)
        
 #Testes JMeter
        
@app.get("/telemetria-redis")
def ultima_telemetria(usuario=Depends(autenticar)):

    dado = redis_client.get(
        "ultima_telemetria"
    )

    if not dado:
        return {}

    return json.loads(dado)

@app.get("/telemetria-mongo")
def telemetria(usuario=Depends(autenticar)):

    dado = col.find_one(
        sort=[("timestamp", -1)]
    )

    if not dado:
        return {}

    dado.pop("_id", None)

    return dado

@app.post("/login")
def login():

    return {
        "token": gerar_token()
    }