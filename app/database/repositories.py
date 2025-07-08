from app.database.connection import DatabaseConnection
from app.core.exceptions import SensorDataNotFoundError
import mysql.connector
import logging

logger = logging.getLogger(__name__)

class SensorRepository:
    @staticmethod
    def get_last_sensor_readings():
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT sr.*, s.type, s.name 
            FROM sensor_readings sr
            JOIN sensors s ON sr.sensor_id = s.id
            WHERE sr.id IN (
                SELECT MAX(id) 
                FROM sensor_readings 
                GROUP BY sensor_id
            )
            ORDER BY s.id
            """
            logger.debug(f"Ejecutando query: {query}")
            cursor.execute(query)
            result = cursor.fetchall()
            
            if not result:
                logger.warning("No se encontraron datos de sensores")
                raise SensorDataNotFoundError()
                
            logger.info(f"Obtenidos {len(result)} registros de sensores")
            for row in result:
                logger.debug(f"Dato sensor: {row}")
                
            return result
        except Exception as e:
            logger.error(f"Error en get_last_sensor_readings: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def get_pressure_stats():
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT pressure, recorded_at 
            FROM sensor_readings 
            WHERE recorded_at >= NOW() - INTERVAL 24 HOUR
            AND pressure IS NOT NULL
            ORDER BY recorded_at
            """
            logger.debug(f"Ejecutando query presión: {query}")
            cursor.execute(query)
            result = cursor.fetchall()
            
            if not result:
                logger.warning("No se encontraron datos de presión")
                raise SensorDataNotFoundError()
                
            logger.info(f"Obtenidos {len(result)} registros de presión")
            return {"pressure": [r['pressure'] for r in result], "data": result}
        except Exception as e:
            logger.error(f"Error en get_pressure_stats: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def get_humidity_stats():
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT humidity, recorded_at 
            FROM sensor_readings 
            WHERE recorded_at >= NOW() - INTERVAL 24 HOUR
            AND humidity IS NOT NULL
            ORDER BY recorded_at
            """
            logger.debug(f"Ejecutando query humedad: {query}")
            cursor.execute(query)
            result = cursor.fetchall()
            
            if not result:
                logger.warning("No se encontraron datos de humedad")
                raise SensorDataNotFoundError()
                
            logger.info(f"Obtenidos {len(result)} registros de humedad")
            return {"humidity": [r['humidity'] for r in result], "data": result}
        except Exception as e:
            logger.error(f"Error en get_humidity_stats: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()