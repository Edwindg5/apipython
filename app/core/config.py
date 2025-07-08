from pydantic_settings import BaseSettings
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "44.217.106.193")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "remoto")
    DB_PASS: str = os.getenv("DB_PASS", "tu_password_segura")
    DB_NAME: str = os.getenv("DB_NAME", "integrador")
    
    class Config:
        env_file = ".env"

settings = Settings()
logger.info("✅ Configuración cargada correctamente")
logger.info(f"Conectando a DB: {settings.DB_USER}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")