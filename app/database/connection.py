#fastapi/app/database/connection.py
import mysql.connector
from mysql.connector import pooling
from app.core.config import settings
from app.core.exceptions import DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="auth_pool",
                    pool_size=5,
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    user=settings.DB_USER,
                    password=settings.DB_PASS,
                    database=settings.DB_NAME,
                    autocommit=True
                )
                logger.info("✅ Conexión exitosa con la base de datos")
            except Exception as e:
                logger.error(f"❌ Error al conectar con la base de datos: {e}")
                raise DatabaseConnectionError(f"Error de conexión: {str(e)}")
        return cls._pool

    @classmethod
    def get_connection(cls):
        pool = cls.get_pool()
        try:
            return pool.get_connection()
        except Exception as e:
            raise DatabaseConnectionError(f"Error al obtener conexión: {str(e)}")