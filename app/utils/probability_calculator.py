#fastapi/app/utils/probability_calculator.py
import numpy as np
from scipy import stats
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ProbabilityAnalyzer:
    @staticmethod
    def calculate_joint_probability(data1, data2, bin_size=10):
        """
        Calcula la probabilidad conjunta de dos variables continuas
        usando discretización por bins
        
        Args:
            data1, data2: Arrays con los datos de los sensores
            bin_size: Número de intervalos para discretizar
            
        Returns:
            joint_prob: DataFrame con las probabilidades conjuntas
            bins1, bins2: Límites de los intervalos usados
        """
        try:
            # Discretización de los datos
            _, bins1 = pd.cut(data1, bins=bin_size, retbins=True)
            _, bins2 = pd.cut(data2, bins=bin_size, retbins=True)
            
            # Crear tabla de contingencia
            contingency_table = pd.crosstab(
                pd.cut(data1, bins=bins1),
                pd.cut(data2, bins=bins2),
                normalize=True
            )
            
            logger.info("Probabilidad conjunta calculada exitosamente")
            return contingency_table, bins1, bins2
            
        except Exception as e:
            logger.error(f"Error calculando probabilidad conjunta: {str(e)}")
            raise

    @staticmethod
    def binomial_analysis(data, success_condition, n_trials=None):
        """
        Realiza análisis binomial sobre datos de sensores
        
        Args:
            data: Array con los datos del sensor
            success_condition: Función que define qué es un "éxito"
            n_trials: Número de ensayos (si None, se usa len(data))
            
        Returns:
            Dict con parámetros de la distribución binomial
        """
        try:
            if n_trials is None:
                n_trials = len(data)
            
            successes = sum(1 for x in data if success_condition(x))
            p = successes / n_trials
            
            # Calcular métricas de la distribución
            mean = n_trials * p
            var = n_trials * p * (1 - p)
            std = np.sqrt(var)
            
            logger.info(f"Análisis binomial completado: p={p:.3f}, éxitos={successes}/{n_trials}")
            
            return {
                "n_trials": n_trials,
                "successes": successes,
                "p": p,
                "mean": mean,
                "variance": var,
                "std_dev": std,
                "pmf": [stats.binom.pmf(k, n_trials, p) for k in range(n_trials + 1)]
            }
            
        except Exception as e:
            logger.error(f"Error en análisis binomial: {str(e)}")
            raise