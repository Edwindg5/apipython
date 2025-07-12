#fastapi/app/routers/sensors.py
from fastapi import APIRouter, Depends
from app.services.sensor_service import SensorService
from app.core.exceptions import handle_app_exception

router = APIRouter()

@router.get("/sensors-data")
def get_sensors_data():
    try:
        return SensorService.get_sensor_data()
    except Exception as e:
        handle_app_exception(e)

@router.get("/pressure-stats")
def get_pressure_stats():
    try:
        return SensorService.get_pressure_stats()
    except Exception as e:
        handle_app_exception(e)

@router.get("/humidity-stats")
def get_humidity_stats():
    try:
        return SensorService.get_humidity_stats()
    except Exception as e:
        handle_app_exception(e)

@router.get("/joint-probability")
def get_joint_probability():
    try:
        return SensorService.get_joint_probability_analysis()
    except Exception as e:
        handle_app_exception(e)