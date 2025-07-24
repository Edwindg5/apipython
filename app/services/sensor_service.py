# app/services/sensor_service.py
from app.core.exceptions import SensorDataNotFoundError
from app.database.repositories import SensorRepository
from app.utils.probability_calculator import ProbabilityAnalyzer
from app.utils.stats_calculator import calculate_stats
import numpy as np
import pandas as pd
import logging
import math
from scipy import stats

logger = logging.getLogger(__name__)

class SensorService:
    @staticmethod
    def _ensure_serializable(data):
        """Asegura que los datos sean serializables a JSON, manejando NaN e infinitos"""
        if isinstance(data, (np.generic)):
            val = data.item() if hasattr(data, 'item') else float(data)
            return None if (math.isnan(val) or math.isinf(val)) else val
        elif isinstance(data, (np.ndarray)):
            return [None if (math.isnan(x) or math.isinf(x)) else float(x) for x in data.tolist()]
        elif isinstance(data, float):
            return None if (math.isnan(data) or math.isinf(data)) else data
        elif isinstance(data, dict):
            return {k: SensorService._ensure_serializable(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [SensorService._ensure_serializable(v) for v in data]
        return data

    @staticmethod
    def _safe_calculate_distribution(values, mean=None, std=None):
        """Calcula distribución normal de manera segura"""
        try:
            if not values or len(values) == 0:
                return {"x": [], "y": [], "mean": None, "std": None}
            
            # Filtrar valores válidos
            valid_values = np.array([v for v in values if not (math.isnan(v) or math.isinf(v))])
            
            if len(valid_values) == 0:
                logger.warning("No hay valores válidos para distribución")
                return {"x": [], "y": [], "mean": None, "std": None}
            
            if len(valid_values) == 1:
                logger.warning("Solo un valor válido, no se puede calcular distribución")
                return {
                    "x": [float(valid_values[0])],
                    "y": [1.0],
                    "mean": float(valid_values[0]),
                    "std": 0.0
                }
            
            # Calcular parámetros si no se proporcionaron
            if mean is None:
                mean = np.mean(valid_values)
            if std is None:
                std = np.std(valid_values, ddof=1)
            
            # Verificar que std sea válido
            if std == 0 or not np.isfinite(std):
                logger.warning("Desviación estándar inválida, usando distribución uniforme")
                return {
                    "x": valid_values.tolist(),
                    "y": [1.0/len(valid_values)] * len(valid_values),
                    "mean": float(mean),
                    "std": None
                }
            
            # Generar puntos para la curva de Gauss
            x_min = np.min(valid_values) - std
            x_max = np.max(valid_values) + std
            x = np.linspace(x_min, x_max, 100)
            y = stats.norm.pdf(x, mean, std)
            
            # Filtrar valores inválidos en el PDF
            valid_indices = np.isfinite(y)
            x = x[valid_indices]
            y = y[valid_indices]
            
            return {
                "x": x.tolist(),
                "y": y.tolist(),
                "mean": float(mean) if np.isfinite(mean) else None,
                "std": float(std) if np.isfinite(std) else None
            }
            
        except Exception as e:
            logger.error(f"Error calculando distribución: {str(e)}")
            return {"x": [], "y": [], "mean": None, "std": None}

    @staticmethod
    def _safe_calculate_histogram(values, bins=10):
        """Calcula histograma de manera segura"""
        try:
            if not values or len(values) == 0:
                return {"bins": [], "counts": []}
            
            # Filtrar valores válidos
            valid_values = np.array([v for v in values if not (math.isnan(v) or math.isinf(v))])
            
            if len(valid_values) == 0:
                return {"bins": [], "counts": []}
            
            if len(valid_values) == 1:
                return {
                    "bins": [float(valid_values[0]), float(valid_values[0]) + 0.1],
                    "counts": [1.0]
                }
            
            # Calcular histograma con densidad
            hist, bin_edges = np.histogram(valid_values, bins=min(bins, len(valid_values)), density=True)
            
            # Filtrar valores inválidos
            hist = np.array([0.0 if (math.isnan(h) or math.isinf(h)) else float(h) for h in hist])
            bin_edges = np.array([float(b) if np.isfinite(b) else 0.0 for b in bin_edges])
            
            return {
                "bins": bin_edges.tolist(),
                "counts": hist.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculando histograma: {str(e)}")
            return {"bins": [], "counts": []}

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
                    "voltage": float(sensor['voltage']) if sensor['voltage'] is not None else None,
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
                
            pressure_values = [float(r['pressure']) for r in data if r['pressure'] is not None]
            
            if not pressure_values:
                raise SensorDataNotFoundError("Todos los valores de presión son NULL")
                
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
                "data": pressure_values[-10:] if len(pressure_values) > 10 else pressure_values
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
                
            humidity_values = [float(r['humidity']) for r in data if r['humidity'] is not None]
            
            if not humidity_values:
                raise SensorDataNotFoundError("Todos los valores de humedad son NULL")
                
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
                "data": humidity_values[-10:] if len(humidity_values) > 10 else humidity_values
            })
        except Exception as e:
            logger.error(f"Error en get_humidity_stats: {str(e)}")
            raise

    @staticmethod
    def get_temperature_stats():
        try:
            logger.info("Calculando estadísticas de temperatura...")
            data = SensorRepository.get_last_50_temperature_readings()
            
            if not data:
                raise SensorDataNotFoundError("No hay datos de temperatura disponibles")
                
            temp_values = [float(r['temperature']) for r in data if r['temperature'] is not None]
            
            if not temp_values:
                raise SensorDataNotFoundError("Todos los valores de temperatura son NULL")
                
            stats = calculate_stats(temp_values)
            enhanced_stats = ProbabilityAnalyzer.calculate_advanced_stats(temp_values)
            
            prob_analysis = {
                "binomial": ProbabilityAnalyzer.binomial_analysis(
                    np.array(temp_values),
                    lambda x: x > np.mean(temp_values)
                ),
                "normal": ProbabilityAnalyzer.normal_distribution_analysis(
                    np.array(temp_values))
            }
            
            return SensorService._ensure_serializable({
                "basic_stats": stats,
                "advanced_stats": enhanced_stats,
                "probability_analysis": prob_analysis,
                "sample_size": len(temp_values),
                "data": temp_values[-10:] if len(temp_values) > 10 else temp_values
            })
        except Exception as e:
            logger.error(f"Error en get_temperature_stats: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_voltage_stats():
        try:
            logger.info("Calculando estadísticas de voltaje...")
            data = SensorRepository.get_last_50_voltage_readings()
            
            if not data:
                raise SensorDataNotFoundError("No hay datos de voltaje disponibles")
                
            voltage_values = [float(r['voltage']) for r in data if r['voltage'] is not None]
            
            if not voltage_values:
                raise SensorDataNotFoundError("Todos los valores de voltaje son NULL")
                
            stats = calculate_stats(voltage_values)
            enhanced_stats = ProbabilityAnalyzer.calculate_advanced_stats(voltage_values)
            
            prob_analysis = {
                "binomial": ProbabilityAnalyzer.binomial_analysis(
                    np.array(voltage_values),
                    lambda x: x > 0.5
                ),
                "normal": ProbabilityAnalyzer.normal_distribution_analysis(
                    np.array(voltage_values))
            }
            
            return SensorService._ensure_serializable({
                "basic_stats": stats,
                "advanced_stats": enhanced_stats,
                "probability_analysis": prob_analysis,
                "sample_size": len(voltage_values),
                "data": voltage_values[-10:] if len(voltage_values) > 10 else voltage_values
            })
        except Exception as e:
            logger.error(f"Error en get_voltage_stats: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_joint_probability_analysis():
        try:
            logger.info("Calculando probabilidad conjunta humedad-presión...")
            
            humidity = SensorRepository.get_last_50_humidity_readings()
            pressure = SensorRepository.get_last_50_pressure_readings()
            
            if not humidity or not pressure:
                raise SensorDataNotFoundError("Datos insuficientes para análisis conjunto")
                
            h_values = np.array([float(x['humidity']) for x in humidity if x['humidity'] is not None])
            p_values = np.array([float(x['pressure']) for x in pressure if x['pressure'] is not None])
            
            if len(h_values) == 0 or len(p_values) == 0:
                raise SensorDataNotFoundError("Datos insuficientes después de filtrar NULLs")
            
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

    @staticmethod
    def get_pressure_distribution(days: int = 7):
        """
        Obtiene datos de presión para generar una distribución normal (campana de Gauss)
        y un histograma para visualización en el frontend.
        """
        try:
            logger.info(f"Obteniendo distribución de presión para últimos {days} días...")
            raw_data = SensorRepository.get_pressure_history(days)
            
            if not raw_data:
                raise SensorDataNotFoundError("No hay datos de presión disponibles")
                
            # Extraer valores y timestamps, filtrando NULLs
            pressure_values = [float(r['pressure']) for r in raw_data if r['pressure'] is not None]
            timestamps = [r['recorded_at'].isoformat() for r in raw_data if r['pressure'] is not None]
            
            if not pressure_values:
                raise SensorDataNotFoundError("Todos los valores de presión son NULL")

            # Calcular distribución y histograma de manera segura
            distribution = SensorService._safe_calculate_distribution(pressure_values)
            histogram = SensorService._safe_calculate_histogram(pressure_values)
            
            # Construir respuesta
            response = {
                "distribution": distribution,
                "histogram": histogram,
                "raw_data": {
                    "values": pressure_values,
                    "timestamps": timestamps
                },
                "metadata": {
                    "days": days,
                    "data_points": len(pressure_values),
                    "date_range": {
                        "start": timestamps[0] if timestamps else None,
                        "end": timestamps[-1] if timestamps else None
                    }
                }
            }
            
            return SensorService._ensure_serializable(response)
            
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error en get_pressure_distribution: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_temperature_distribution(days: int = 7):
        """
        Obtiene datos de temperatura para generar una distribución normal (campana de Gauss)
        y un histograma para visualización en el frontend.
        """
        try:
            logger.info(f"Obteniendo distribución de temperatura para últimos {days} días...")
            raw_data = SensorRepository.get_temperature_history(days)
            
            if not raw_data:
                raise SensorDataNotFoundError("No hay datos de temperatura disponibles")
                
            # Extraer valores y timestamps, filtrando NULLs
            temp_values = [float(r['temperature']) for r in raw_data if r['temperature'] is not None]
            timestamps = [r['recorded_at'].isoformat() for r in raw_data if r['temperature'] is not None]
            
            if not temp_values:
                raise SensorDataNotFoundError("Todos los valores de temperatura son NULL")

            # Calcular distribución y histograma de manera segura
            distribution = SensorService._safe_calculate_distribution(temp_values)
            histogram = SensorService._safe_calculate_histogram(temp_values)
            
            # Construir respuesta
            response = {
                "distribution": distribution,
                "histogram": histogram,
                "raw_data": {
                    "values": temp_values,
                    "timestamps": timestamps
                },
                "metadata": {
                    "days": days,
                    "data_points": len(temp_values),
                    "date_range": {
                        "start": timestamps[0] if timestamps else None,
                        "end": timestamps[-1] if timestamps else None
                    }
                }
            }
            
            return SensorService._ensure_serializable(response)
            
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error en get_temperature_distribution: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_humidity_distribution(days: int = 7):
        """
        Obtiene datos de humedad para generar una distribución normal (campana de Gauss)
        y un histograma para visualización en el frontend.
        """
        try:
            logger.info(f"Obteniendo distribución de humedad para últimos {days} días...")
            raw_data = SensorRepository.get_humidity_history(days)
            
            if not raw_data:
                raise SensorDataNotFoundError("No hay datos de humedad disponibles")
                
            # Extraer valores y timestamps, filtrando NULLs
            humidity_values = [float(r['humidity']) for r in raw_data if r['humidity'] is not None]
            timestamps = [r['recorded_at'].isoformat() for r in raw_data if r['humidity'] is not None]
            
            if not humidity_values:
                raise SensorDataNotFoundError("Todos los valores de humedad son NULL")

            # Calcular distribución y histograma de manera segura
            distribution = SensorService._safe_calculate_distribution(humidity_values)
            histogram = SensorService._safe_calculate_histogram(humidity_values)
            
            # Construir respuesta
            response = {
                "distribution": distribution,
                "histogram": histogram,
                "raw_data": {
                    "values": humidity_values,
                    "timestamps": timestamps
                },
                "metadata": {
                    "days": days,
                    "data_points": len(humidity_values),
                    "date_range": {
                        "start": timestamps[0] if timestamps else None,
                        "end": timestamps[-1] if timestamps else None
                    }
                }
            }
            
            return SensorService._ensure_serializable(response)
            
        except SensorDataNotFoundError as e:
            logger.warning(str(e))
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error en get_humidity_distribution: {str(e)}", exc_info=True)
            raise