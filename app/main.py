#fastapi/app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sensors
from app.core.exceptions import handle_app_exception
from app.database.connection import DatabaseConnection
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