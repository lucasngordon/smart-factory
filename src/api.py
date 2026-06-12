from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import asyncio

# -------------------------
# MONGO
# -------------------------
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI não configurada")

client = MongoClient(MONGO_URI)
db = client["smart_factory"]
col = db["telemetria"]

# -------------------------
# FASTAPI
# -------------------------
app = FastAPI()

# -------------------------
# DASHBOARD HTML
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

            .temp { color: #f87171; font-size: 32px; }
            .vib { color: #60a5fa; font-size: 32px; }
            .eng { color: #34d399; font-size: 32px; }
            
        </style>
    </head>

    <body>

        <h1>🏭 Smart Factory Dashboard</h1>

        <!-- TEMPO REAL -->
        <div class="container">
            <div class="card">
                <h2>Temperatura</h2>
                <div id="temp" class="temp">--</div>
            </div>

            <div class="card">
                <h2>Vibração</h2>
                <div id="vib" class="vib">--</div>
            </div>

            <div class="card">
                <h2>Energia</h2>
                <div id="eng" class="eng">--</div>
            </div>
        </div>

        <script>
            // -------------------------
            // WEBSOCKET TEMPO REAL
            // -------------------------
            const ws = new WebSocket("ws://localhost:8000/ws");

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);

                document.getElementById("temp").innerText =
                    Number(data.temperatura).toFixed(1) + " °C";

                document.getElementById("vib").innerText =
                    Number(data.vibracao).toFixed(2) + " mm/s";

                document.getElementById("eng").innerText =
                    Number(data.energia).toFixed(2) + " kW";
            };
        </script>

    </body>
    </html>
    """

# -------------------------
# WEBSOCKET
# -------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            dado = col.find_one(sort=[("timestamp", -1)])

            if dado:
                await websocket.send_json({
                    "temperatura": dado.get("temperatura"),
                    "vibracao": dado.get("vibracao"),
                    "energia": dado.get("energia")
                })

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("Cliente desconectado")