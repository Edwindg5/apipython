from app.database.repositories import SensorRepository
from app.core.exceptions import SensorDataNotFoundError
from app.utils.stats_calculator import calculate_stats
from app.routers.websocket import manager  # Nueva importación
import logging
import asyncio

logger = logging.getLogger(__name__)

class SensorService:
    @staticmethod
    def get_sensor_data():
        try:
            logger.info("Obteniendo datos de sensores...")
            data = SensorRepository.get_last_sensor_readings()
            logger.info("Datos de sensores obtenidos correctamente")
            
            # Procesar datos para mejor presentación
            processed_data = []
            for sensor in data:
                processed = {
                    "id": sensor['id'],
                    "sensor_id": sensor['sensor_id'],
                    "sensor_name": sensor['name'],
                    "sensor_type": sensor['type'],
                    "temperature": sensor['temperature'],
                    "humidity": sensor['humidity'],
                    "pressure": sensor['pressure'],
                    "recorded_at": sensor['recorded_at'].isoformat() if sensor['recorded_at'] else None
                }
                processed_data.append(processed)
            
            return {"sensors": processed_data}
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error inesperado en get_sensor_data: {str(e)}")
            raise

    @staticmethod
    def get_pressure_stats():
        try:
            logger.info("Calculando estadísticas de presión...")
            data = SensorRepository.get_pressure_stats()
            
            if not data['pressure']:
                raise SensorDataNotFoundError("No hay datos de presión disponibles")
                
            stats = calculate_stats(data['pressure'])
            logger.info(f"Estadísticas de presión calculadas: {stats}")
            
            # Formatear fechas para respuesta JSON
            formatted_data = []
            for entry in data['data']:
                formatted_entry = entry.copy()
                formatted_entry['recorded_at'] = entry['recorded_at'].isoformat() if entry['recorded_at'] else None
                formatted_data.append(formatted_entry)
            
            return {
                "stats": stats,
                "data": formatted_data
            }
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error inesperado en get_pressure_stats: {str(e)}")
            raise

    @staticmethod
    def get_humidity_stats():
        try:
            logger.info("Calculando estadísticas de humedad...")
            data = SensorRepository.get_humidity_stats()
            
            if not data['humidity']:
                raise SensorDataNotFoundError("No hay datos de humedad disponibles")
                
            stats = calculate_stats(data['humidity'])
            logger.info(f"Estadísticas de humedad calculadas: {stats}")
            
            # Formatear fechas para respuesta JSON
            formatted_data = []
            for entry in data['data']:
                formatted_entry = entry.copy()
                formatted_entry['recorded_at'] = entry['recorded_at'].isoformat() if entry['recorded_at'] else None
                formatted_data.append(formatted_entry)
            
            return {
                "stats": stats,
                "data": formatted_data
            }
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error inesperado en get_humidity_stats: {str(e)}")
            raise
    @staticmethod
    async def broadcast_humidity_update():
        """Envía una actualización de humedad a todos los clientes WebSocket conectados"""
        try:
            humidity_data = SensorService.get_humidity_stats()
            await manager.broadcast({
                "type": "humidity_update",
                "data": humidity_data
            })
        except Exception as e:
            logger.error(f"Error broadcasting humidity update: {str(e)}")