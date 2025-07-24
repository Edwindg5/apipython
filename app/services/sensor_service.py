# app/services/sensor_service.py
from app.core.exceptions import SensorDataNotFoundError
from app.database.repositories import SensorRepository
from app.utils.probability_calculator import ProbabilityAnalyzer
from app.utils.stats_calculator import calculate_stats
import numpy as np
import pandas as pd
import logging
from scipy import stats

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
        
        Args:
            days: Número de días de datos históricos a recuperar
            
        Returns:
            dict: Contiene:
                - distribution: puntos para la curva de Gauss (x, y)
                - histogram: datos para el histograma (bins, counts)
                - raw_data: valores y timestamps originales
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
                
            # Calcular parámetros de la distribución normal
            mean = np.mean(pressure_values)
            std = np.std(pressure_values)
            
            # Generar puntos para la curva de Gauss
            x = np.linspace(min(pressure_values), max(pressure_values), 100)
            y = stats.norm.pdf(x, mean, std)
            
            # Preparar datos para el histograma
            hist, bin_edges = np.histogram(pressure_values, bins=10, density=True)
            
            # Construir respuesta
            response = {
                "distribution": {
                    "x": x.tolist(),
                    "y": y.tolist(),
                    "mean": float(mean),
                    "std": float(std)
                },
                "histogram": {
                    "bins": bin_edges.tolist(),
                    "counts": hist.tolist()
                },
                "raw_data": {
                    "values": pressure_values,
                    "timestamps": timestamps
                },
                "metadata": {
                    "days": days,
                    "data_points": len(pressure_values),
                    "date_range": {
                        "start": timestamps[0],
                        "end": timestamps[-1]
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
        
        Args:
            days: Número de días de datos históricos a recuperar
            
        Returns:
            dict: Contiene:
                - distribution: puntos para la curva de Gauss (x, y)
                - histogram: datos para el histograma (bins, counts)
                - raw_data: valores y timestamps originales
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
                
            # Calcular parámetros de la distribución normal
            mean = np.mean(temp_values)
            std = np.std(temp_values)
            
            # Generar puntos para la curva de Gauss
            x = np.linspace(min(temp_values), max(temp_values), 100)
            y = stats.norm.pdf(x, mean, std)
            
            # Preparar datos para el histograma
            hist, bin_edges = np.histogram(temp_values, bins=10, density=True)
            
            # Construir respuesta
            response = {
                "distribution": {
                    "x": x.tolist(),
                    "y": y.tolist(),
                    "mean": float(mean),
                    "std": float(std)
                },
                "histogram": {
                    "bins": bin_edges.tolist(),
                    "counts": hist.tolist()
                },
                "raw_data": {
                    "values": temp_values,
                    "timestamps": timestamps
                },
                "metadata": {
                    "days": days,
                    "data_points": len(temp_values),
                    "date_range": {
                        "start": timestamps[0],
                        "end": timestamps[-1]
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
        
        Args:
            days: Número de días de datos históricos a recuperar
            
        Returns:
            dict: Contiene:
                - distribution: puntos para la curva de Gauss (x, y)
                - histogram: datos para el histograma (bins, counts)
                - raw_data: valores y timestamps originales
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
                
            # Calcular parámetros de la distribución normal
            mean = np.mean(humidity_values)
            std = np.std(humidity_values)
            
            # Generar puntos para la curva de Gauss
            x = np.linspace(min(humidity_values), max(humidity_values), 100)
            y = stats.norm.pdf(x, mean, std)
            
            # Preparar datos para el histograma
            hist, bin_edges = np.histogram(humidity_values, bins=10, density=True)
            
            # Construir respuesta
            response = {
                "distribution": {
                    "x": x.tolist(),
                    "y": y.tolist(),
                    "mean": float(mean),
                    "std": float(std)
                },
                "histogram": {
                    "bins": bin_edges.tolist(),
                    "counts": hist.tolist()
                },
                "raw_data": {
                    "values": humidity_values,
                    "timestamps": timestamps
                },
                "metadata": {
                    "days": days,
                    "data_points": len(humidity_values),
                    "date_range": {
                        "start": timestamps[0],
                        "end": timestamps[-1]
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