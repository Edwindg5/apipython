#fastapi/app/services/sensor_service.py
from app.core.exceptions import SensorDataNotFoundError
from app.database.repositories import SensorRepository
from app.utils.probability_calculator import ProbabilityAnalyzer
from app.utils.stats_calculator import calculate_stats
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class SensorService:
    @staticmethod
    def _ensure_serializable(data):
        """Asegura que los datos sean serializables a JSON"""
        if isinstance(data, (np.generic)):
            return data.item() if hasattr(data, 'item') else float(data)
        elif isinstance(data, (np.ndarray)):
            return data.tolist()
        elif isinstance(data, dict):
            return {k: SensorService._ensure_serializable(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [SensorService._ensure_serializable(v) for v in data]
        return data

    @staticmethod
    def get_sensor_data():
        try:
            logger.info("Obteniendo datos de sensores...")
            data = SensorRepository.get_last_sensor_readings()
            
            processed_data = []
            for sensor in data:
                processed = {
                    "id": sensor['id'],
                    "sensor_id": sensor['sensor_id'],
                    "sensor_name": sensor['name'],
                    "sensor_type": sensor['type'],
                    "temperature": float(sensor['temperature']) if sensor['temperature'] is not None else None,
                    "humidity": float(sensor['humidity']) if sensor['humidity'] is not None else None,
                    "pressure": float(sensor['pressure']) if sensor['pressure'] is not None else None,
                    "recorded_at": sensor['recorded_at'].isoformat() if sensor['recorded_at'] else None
                }
                processed_data.append(processed)
            
            return {"sensors": processed_data}
        except Exception as e:
            logger.error(f"Error en get_sensor_data: {str(e)}")
            raise

    @staticmethod
    def get_pressure_stats():
        try:
            logger.info("Calculando estadísticas de presión...")
            data = SensorRepository.get_last_50_pressure_readings()
            
            if not data:
                raise SensorDataNotFoundError("No hay datos de presión disponibles")
                
            pressure_values = [float(r['pressure']) for r in data]
            
            stats = calculate_stats(pressure_values)
            enhanced_stats = ProbabilityAnalyzer.calculate_advanced_stats(pressure_values)
            
            prob_analysis = {
                "binomial": ProbabilityAnalyzer.binomial_analysis(
                    np.array(pressure_values),
                    lambda x: x > np.mean(pressure_values)
                ),
                "normal": ProbabilityAnalyzer.normal_distribution_analysis(
                    np.array(pressure_values))
            }
            
            return SensorService._ensure_serializable({
                "basic_stats": stats,
                "advanced_stats": enhanced_stats,
                "probability_analysis": prob_analysis,
                "sample_size": len(pressure_values),
                "data": pressure_values[-10:]
            })
        except Exception as e:
            logger.error(f"Error en get_pressure_stats: {str(e)}")
            raise

    @staticmethod
    def get_humidity_stats():
        try:
            logger.info("Calculando estadísticas de humedad...")
            data = SensorRepository.get_last_50_humidity_readings()
            
            if not data:
                raise SensorDataNotFoundError("No hay datos de humedad disponibles")
                
            humidity_values = [float(r['humidity']) for r in data]
            
            stats = calculate_stats(humidity_values)
            enhanced_stats = ProbabilityAnalyzer.calculate_advanced_stats(humidity_values)
            
            prob_analysis = {
                "binomial": ProbabilityAnalyzer.binomial_analysis(
                    np.array(humidity_values),
                    lambda x: x > 80
                ),
                "normal": ProbabilityAnalyzer.normal_distribution_analysis(
                    np.array(humidity_values))
            }
            
            return SensorService._ensure_serializable({
                "basic_stats": stats,
                "advanced_stats": enhanced_stats,
                "probability_analysis": prob_analysis,
                "sample_size": len(humidity_values),
                "data": humidity_values[-10:]
            })
        except Exception as e:
            logger.error(f"Error en get_humidity_stats: {str(e)}")
            raise

    @staticmethod
    def get_joint_probability_analysis():
        try:
            logger.info("Calculando probabilidad conjunta humedad-presión...")
            
            humidity = SensorRepository.get_last_50_humidity_readings()
            pressure = SensorRepository.get_last_50_pressure_readings()
            
            if not humidity or not pressure:
                raise SensorDataNotFoundError("Datos insuficientes para análisis conjunto")
                
            h_values = np.array([float(x['humidity']) for x in humidity])
            p_values = np.array([float(x['pressure']) for x in pressure])
            
            # Calcular probabilidad conjunta
            joint_prob = ProbabilityAnalyzer.calculate_joint_probability(
                h_values, p_values, bin_size=5
            )
            
            # Calcular media de presión una vez para evitar recalcular
            pressure_mean = float(np.mean(p_values))
            
            # Análisis binomial con condiciones corregidas
            binomial_h = ProbabilityAnalyzer.binomial_analysis(
                h_values,
                lambda x: x > 80  # Éxito = humedad > 80%
            )
            
            binomial_p = ProbabilityAnalyzer.binomial_analysis(
                p_values,
                lambda x: x > pressure_mean  # Éxito = presión > media
            )
            
            # Estadísticas avanzadas
            stats_h = ProbabilityAnalyzer.calculate_advanced_stats(h_values)
            stats_p = ProbabilityAnalyzer.calculate_advanced_stats(p_values)
            
            # Preparar respuesta asegurando serialización
            response = {
                "joint_probability": joint_prob,
                "binomial_analysis": {
                    "humidity": binomial_h,
                    "pressure": binomial_p
                },
                "advanced_stats": {
                    "humidity": stats_h,
                    "pressure": stats_p
                },
                "data_points": int(len(h_values))
            }
            
            return SensorService._ensure_serializable(response)
            
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error en get_joint_probability_analysis: {str(e)}", exc_info=True)
            raise