from fastapi import APIRouter, HTTPException
from app.services.sensor_service import SensorService
from app.core.exceptions import handle_app_exception
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def _handle_service_error(e, endpoint_name):
    """Maneja errores de servicio de manera consistente"""
    logger.error(f"Error en {endpoint_name}: {str(e)}", exc_info=True)
    try:
        return handle_app_exception(e)
    except Exception:
        # Si handle_app_exception falla, devolver error HTTP genérico
        raise HTTPException(status_code=500, detail=f"Error interno en {endpoint_name}")

@router.get("/sensors-data")
def get_sensors_data():
    try:
        result = SensorService.get_sensor_data()
        return result
    except Exception as e:
        return _handle_service_error(e, "sensors-data")

@router.get("/pressure-stats")
def get_pressure_stats():
    try:
        result = SensorService.get_pressure_stats()
        return result
    except Exception as e:
        return _handle_service_error(e, "pressure-stats")

@router.get("/humidity-stats")
def get_humidity_stats():
    try:
        result = SensorService.get_humidity_stats()
        return result
    except Exception as e:
        return _handle_service_error(e, "humidity-stats")

@router.get("/temperature-stats")
def get_temperature_stats():
    try:
        result = SensorService.get_temperature_stats()
        return result
    except Exception as e:
        return _handle_service_error(e, "temperature-stats")

@router.get("/voltage-stats")
def get_voltage_stats():
    try:
        result = SensorService.get_voltage_stats()
        return result
    except Exception as e:
        return _handle_service_error(e, "voltage-stats")

@router.get("/joint-probability")
def get_joint_probability():
    try:
        result = SensorService.get_joint_probability_analysis()
        return result
    except Exception as e:
        return _handle_service_error(e, "joint-probability")

@router.get("/pressure-distribution/{days}")
def get_pressure_distribution(days: int = 7):
    try:
        if days <= 0 or days > 365:
            raise HTTPException(status_code=400, detail="Los días deben estar entre 1 y 365")
        
        result = SensorService.get_pressure_distribution(days)
        return result
    except HTTPException:
        raise
    except Exception as e:
        return _handle_service_error(e, "pressure-distribution")

@router.get("/temperature-distribution")
def get_temperature_distribution(days: int = 7):
    try:
        if days <= 0 or days > 365:
            raise HTTPException(status_code=400, detail="Los días deben estar entre 1 y 365")
        
        result = SensorService.get_temperature_distribution(days)
        return result
    except HTTPException:
        raise
    except Exception as e:
        return _handle_service_error(e, "temperature-distribution")

@router.get("/humidity-distribution")
def get_humidity_distribution(days: int = 7):
    try:
        if days <= 0 or days > 365:
            raise HTTPException(status_code=400, detail="Los días deben estar entre 1 y 365")
        
        result = SensorService.get_humidity_distribution(days)
        return result
    except HTTPException:
        raise
    except Exception as e:
        return _handle_service_error(e, "humidity-distribution")