#fastapi/app/services/sensor_service.py
from app.core.exceptions import SensorDataNotFoundError
from app.database.repositories import SensorRepository
from app.utils.probability_calculator import ProbabilityAnalyzer
from app.utils.stats_calculator import calculate_stats
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SensorService:
    @staticmethod
    def get_sensor_data():
        try:
            logger.info("Obteniendo datos de sensores...")
            data = SensorRepository.get_last_sensor_readings()
            logger.info("Datos de sensores obtenidos correctamente")
            
            # Procesar datos para mejor presentación
            processed_data = []
            for sensor in data:
                processed = {
                    "id": sensor['id'],
                    "sensor_id": sensor['sensor_id'],
                    "sensor_name": sensor['name'],
                    "sensor_type": sensor['type'],
                    "temperature": sensor['temperature'],
                    "humidity": sensor['humidity'],
                    "pressure": sensor['pressure'],
                    "recorded_at": sensor['recorded_at'].isoformat() if sensor['recorded_at'] else None
                }
                processed_data.append(processed)
            
            return {"sensors": processed_data}
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error inesperado en get_sensor_data: {str(e)}")
            raise

    @staticmethod
    def get_pressure_stats():
        try:
            logger.info("Calculando estadísticas de presión...")
            data = SensorRepository.get_pressure_stats()
            
            if not data['pressure']:
                raise SensorDataNotFoundError("No hay datos de presión disponibles")
                
            stats = calculate_stats(data['pressure'])
            
            # Nuevos cálculos de probabilidad
            pressure_values = np.array(data['pressure'])
            prob_analysis = {
                "probability_analysis": {
                    "binomial": ProbabilityAnalyzer.binomial_analysis(
                        pressure_values,
                        lambda x: x > np.mean(pressure_values)  # Éxito = presión > media
                    )
                }
            }
            
            logger.info(f"Estadísticas de presión calculadas: {stats}")
            
            formatted_data = []
            for entry in data['data']:
                formatted_entry = entry.copy()
                formatted_entry['recorded_at'] = entry['recorded_at'].isoformat() if entry['recorded_at'] else None
                formatted_data.append(formatted_entry)
            
            return {
                "stats": stats,
                "probability": prob_analysis,
                "data": formatted_data
            }
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error inesperado en get_pressure_stats: {str(e)}")
            raise

    @staticmethod
    def get_humidity_stats():
        try:
            logger.info("Calculando estadísticas de humedad...")
            data = SensorRepository.get_humidity_stats()
            
            if not data['humidity']:
                raise SensorDataNotFoundError("No hay datos de humedad disponibles")
                
            stats = calculate_stats(data['humidity'])
            
            # Nuevos cálculos de probabilidad
            humidity_values = np.array(data['humidity'])
            prob_analysis = {
                "probability_analysis": {
                    "binomial": ProbabilityAnalyzer.binomial_analysis(
                        humidity_values,
                        lambda x: x > 80  # Éxito = humedad > 80%
                    )
                }
            }
            
            logger.info(f"Estadísticas de humedad calculadas: {stats}")
            
            formatted_data = []
            for entry in data['data']:
                formatted_entry = entry.copy()
                formatted_entry['recorded_at'] = entry['recorded_at'].isoformat() if entry['recorded_at'] else None
                formatted_data.append(formatted_entry)
            
            return {
                "stats": stats,
                "probability": prob_analysis,
                "data": formatted_data
            }
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error inesperado en get_humidity_stats: {str(e)}")
            raise

    @staticmethod
    def get_joint_probability_analysis(days: int = 7):
        try:
            logger.info("Calculando probabilidad conjunta humedad-presión...")
            
            # Obtener datos históricos
            humidity_data = SensorRepository.get_humidity_history(days)
            pressure_data = SensorRepository.get_pressure_history(days)
            
            if not humidity_data or not pressure_data:
                raise SensorDataNotFoundError("Datos insuficientes para análisis conjunto")
                
            # Convertir a arrays numpy
            h_values = np.array([x['humidity'] for x in humidity_data])
            p_values = np.array([x['pressure'] for x in pressure_data])
            
            # Calcular probabilidad conjunta
            joint_prob, bins_h, bins_p = ProbabilityAnalyzer.calculate_joint_probability(
                h_values, p_values
            )
            
            # Calcular análisis binomial para humedad
            binomial_h = ProbabilityAnalyzer.binomial_analysis(
                h_values,
                lambda x: x > 80  # Éxito = humedad > 80%
            )
            
            # Calcular análisis binomial para presión
            binomial_p = ProbabilityAnalyzer.binomial_analysis(
                p_values,
                lambda x: x > np.mean(p_values)  # Éxito = presión > media
            )
            
            return {
                "joint_probability": {
                    "table": joint_prob.to_dict(),
                    "humidity_bins": bins_h.tolist(),
                    "pressure_bins": bins_p.tolist()
                },
                "binomial_analysis": {
                    "humidity": binomial_h,
                    "pressure": binomial_p
                },
                "data_points": len(h_values)
            }
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"message": str(e)}
        except Exception as e:
            logger.error(f"Error en get_joint_probability_analysis: {str(e)}")
            raise