#fastapi/app\main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sensors
from app.routers.websocket import router as websocket_router
from app.core.exceptions import handle_app_exception
from app.database.connection import DatabaseConnection
from app.utils.background_tasks import periodic_humidity_broadcast
import logging

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(sensors.router, prefix="/api")

app.include_router(websocket_router)

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Iniciando aplicación...")
        # Test connection
        conn = DatabaseConnection.get_connection()
        conn.close()
        logger.info("✅ Conexión a BD verificada correctamente")
    except Exception as e:
        logger.error(f"❌ Error inicial al conectar con BD: {e}")

@app.get("/")
def read_root():
    logger.info("Solicitud recibida en endpoint raíz")
    return {"message": "API de Sensores en funcionamiento"}

# Manejo global de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Excepción no manejada: {str(exc)}")
    return handle_app_exception(exc)

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Iniciando aplicación...")
        # Test connection
        conn = DatabaseConnection.get_connection()
        conn.close()
        logger.info("✅ Conexión a BD verificada correctamente")
        
        # Iniciar tarea de WebSocket en segundo plano
        asyncio.create_task(periodic_humidity_broadcast())
        logger.info("✅ Tarea de WebSocket para humedad iniciada")
    except Exception as e:
        logger.error(f"❌ Error inicial al conectar con BD: {e}")