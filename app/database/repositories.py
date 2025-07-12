#fastapi/app/database/repositories.py
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
            WHERE sensor_id = 6
            AND recorded_at >= NOW() - INTERVAL 7 DAY
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
            WHERE sensor_id = 5
            AND recorded_at >= NOW() - INTERVAL 7 DAY
            AND humidity IS NOT NULL
            ORDER BY recorded_at
            """
            logger.debug(f"Ejecutando query humedad: {query}")
            cursor.execute(query)
            result = cursor.fetchall()
            
            logger.debug(f"Resultados crudos: {result}")
            
            if not result:
                logger.warning("No se encontraron datos de humedad")
                raise SensorDataNotFoundError()
                
            logger.info(f"Obtenidos {len(result)} registros de humedad")
            return {"humidity": [r['humidity'] for r in result], "data": result}
        except Exception as e:
            logger.error(f"Error en get_humidity_stats: {str(e)}", exc_info=True)
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                
    @staticmethod
    def get_humidity_history(days: int = 7):
        """Obtiene datos históricos de humedad"""
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT humidity, recorded_at 
            FROM sensor_readings 
            WHERE sensor_id = 5
            AND recorded_at >= NOW() - INTERVAL %s DAY
            AND humidity IS NOT NULL
            ORDER BY recorded_at
            """
            cursor.execute(query, (days,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error en get_humidity_history: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def get_pressure_history(days: int = 7):
        """Obtiene datos históricos de presión"""
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT pressure, recorded_at 
            FROM sensor_readings 
            WHERE sensor_id = 6
            AND recorded_at >= NOW() - INTERVAL %s DAY
            AND pressure IS NOT NULL
            ORDER BY recorded_at
            """
            cursor.execute(query, (days,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error en get_pressure_history: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    @staticmethod
    def get_last_50_humidity_readings():
        """Obtiene los últimos 50 registros de humedad"""
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT humidity, recorded_at 
            FROM sensor_readings 
            WHERE sensor_id = 5
            AND humidity IS NOT NULL
            ORDER BY recorded_at DESC
            LIMIT 50
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error en get_last_50_humidity_readings: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def get_last_50_pressure_readings():
        """Obtiene los últimos 50 registros de presión"""
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT pressure, recorded_at 
            FROM sensor_readings 
            WHERE sensor_id = 6
            AND pressure IS NOT NULL
            ORDER BY recorded_at DESC
            LIMIT 50
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error en get_last_50_pressure_readings: {str(e)}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()