#fastapi/app/services/probability_service.py
from app.database.repositories import SensorRepository
from app.utils.probability_calculator import ProbabilityAnalyzer
from app.core.exceptions import SensorDataNotFoundError
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ProbabilityService:
    @staticmethod
    async def joint_probability_analysis():
        """Analiza probabilidad conjunta de humedad y presión"""
        try:
            logger.info("Iniciando análisis de probabilidad conjunta")
            
            # Obtener datos históricos
            humidity_data = await SensorRepository.get_humidity_history()
            pressure_data = await SensorRepository.get_pressure_history()
            
            if not humidity_data or not pressure_data:
                raise SensorDataNotFoundError("Datos insuficientes para análisis")
            
            # Calcular probabilidad conjunta
            joint_prob, bins_h, bins_p = ProbabilityAnalyzer.calculate_joint_probability(
                np.array([x['humidity'] for x in humidity_data]),
                np.array([x['pressure'] for x in pressure_data])
            )
            
            # Formatear resultados
            return {
                "joint_probability": joint_prob.to_dict(),
                "humidity_bins": bins_h.tolist(),
                "pressure_bins": bins_p.tolist(),
                "analysis_type": "Probabilidad conjunta humedad-presión"
            }
            
        except Exception as e:
            logger.error(f"Error en servicio de probabilidad conjunta: {str(e)}")
            raise

    @staticmethod
    async def binomial_analysis():
        """Analiza distribución binomial de eventos de humedad alta"""
        try:
            logger.info("Iniciando análisis binomial")
            
            # Obtener datos históricos
            humidity_data = await SensorRepository.get_humidity_history()
            
            if not humidity_data:
                raise SensorDataNotFoundError("Datos de humedad no disponibles")
            
            # Definir condición de éxito (humedad > 80%)
            humidity_values = np.array([x['humidity'] for x in humidity_data])
            result = ProbabilityAnalyzer.binomial_analysis(
                humidity_values,
                lambda x: x > 80
            )
            
            return {
                **result,
                "analysis_type": "Distribución binomial de humedad > 80%",
                "success_condition": "Humedad > 80%"
            }
            
        except Exception as e:
            logger.error(f"Error en servicio de análisis binomial: {str(e)}")
            raise