import os
import mysql.connector
from mysql.connector import pooling
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_pool = None

def get_db():
    global db_pool
    
    if db_pool is None:
        logger.info("⏳ Intentando conectar con la base de datos...")
        try:
            db_pool = pooling.MySQLConnectionPool(
                pool_name="auth_pool",
                pool_size=5,  # Reducido para pruebas
                host=os.getenv("DB_HOST", "44.217.106.193"),
                port=int(os.getenv("DB_PORT", "3306")),
                user=os.getenv("DB_USER", "remoto"),
                password=os.getenv("DB_PASS", "tu_password_segura"),
                database=os.getenv("DB_NAME", "integrador"),
                autocommit=True
            )
            logger.info("✅ Conexión exitosa con la base de datos")
        except Exception as e:
            logger.error(f"❌ Error al conectar con la base de datos: {e}")
            raise
    
    return db_pool.get_connection()