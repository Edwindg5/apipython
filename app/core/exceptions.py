#fastapi/app/core/exceptions.py
from fastapi import HTTPException, status

class AppException(Exception):
    """Base exception for the application"""

class DatabaseConnectionError(AppException):
    """Error de conexión a la base de datos"""

class SensorDataNotFoundError(AppException):
    """Datos de sensor no encontrados"""

def handle_app_exception(exc: AppException):
    if isinstance(exc, DatabaseConnectionError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error de conexión con la base de datos"
        )
    elif isinstance(exc, SensorDataNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Datos de sensor no encontrados"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )