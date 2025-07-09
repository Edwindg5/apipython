from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.sensor_service import SensorService
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nueva conexión WebSocket. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Conexión WebSocket cerrada. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje WebSocket: {str(e)}")
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws/humidity")
async def websocket_humidity_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Esperar un pequeño mensaje del cliente para mantener la conexión activa
            # (podríamos también usar ping/pong)
            await websocket.receive_text()
            
            # Obtener datos de humedad
            humidity_data = SensorService.get_humidity_stats()
            
            # Enviar datos al cliente
            await websocket.send_json({
                "type": "humidity_update",
                "data": humidity_data
            })
            
            # Esperar antes de la próxima actualización
            await asyncio.sleep(5)  # Actualizar cada 5 segundos
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en WebSocket: {str(e)}")
        manager.disconnect(websocket)