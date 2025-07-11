#fastapi/app/utils/background_tasks.py
import asyncio
from app.services.sensor_service import SensorService
import logging

logger = logging.getLogger(__name__)

async def periodic_humidity_broadcast(interval: int = 5):
    """Envía actualizaciones periódicas de humedad a través de WebSocket"""
    while True:
        try:
            await SensorService.broadcast_humidity_update()
            logger.debug("Humidity update broadcasted via WebSocket")
        except Exception as e:
            logger.error(f"Error in periodic humidity broadcast: {str(e)}")
        
        await asyncio.sleep(interval)