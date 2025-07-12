#fastapi/app/utils/probability_calculator.py
import numpy as np
from scipy import stats
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ProbabilityAnalyzer:
    @staticmethod
    def _convert_to_native(value):
        """Convierte valores numpy/pandas a tipos nativos de Python"""
        if isinstance(value, (np.generic, pd.Timestamp)):
            return value.item() if hasattr(value, 'item') else value.tolist()
        elif isinstance(value, (np.ndarray, pd.Series, pd.Index)):
            return value.tolist()
        elif isinstance(value, dict):
            return {k: ProbabilityAnalyzer._convert_to_native(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [ProbabilityAnalyzer._convert_to_native(v) for v in value]
        return value

    @staticmethod
    def calculate_joint_probability(data1, data2, bin_size=10):
        """
        Calcula la probabilidad conjunta de dos variables continuas
        """
        try:
            data1_cut, bins1 = pd.cut(data1, bins=bin_size, retbins=True)
            data2_cut, bins2 = pd.cut(data2, bins=bin_size, retbins=True)
            
            data1_str = data1_cut.astype(str)
            data2_str = data2_cut.astype(str)
            
            contingency_table = pd.crosstab(
                data1_str,
                data2_str,
                normalize=True
            )
            
            logger.info("Probabilidad conjunta calculada exitosamente")
            
            # Convertir a tipos nativos
            return {
                "table": contingency_table.to_dict(),
                "bins1": bins1.tolist(),
                "bins2": bins2.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculando probabilidad conjunta: {str(e)}")
            raise

    @staticmethod
    def binomial_analysis(data, success_condition, n_trials=None):
        """
        Realiza análisis binomial sobre datos de sensores
        """
        try:
            if n_trials is None:
                n_trials = len(data)
            
            successes = sum(1 for x in data if success_condition(x))
            p = successes / n_trials
            
            # Convertir a float nativo
            p = float(p)
            mean = float(n_trials * p)
            var = float(n_trials * p * (1 - p))
            std = float(np.sqrt(var))
            
            logger.info(f"Análisis binomial completado: p={p:.3f}, éxitos={successes}/{n_trials}")
            
            result = {
                "n_trials": int(n_trials),
                "successes": int(successes),
                "p": p,
                "mean": mean,
                "variance": var,
                "std_dev": std,
                "pmf": [float(stats.binom.pmf(k, n_trials, p)) for k in range(n_trials + 1)]
            }
            
            return ProbabilityAnalyzer._convert_to_native(result)
            
        except Exception as e:
            logger.error(f"Error en análisis binomial: {str(e)}")
            raise

    @staticmethod
    def normal_distribution_analysis(data):
        """Analiza cómo se ajustan los datos a una distribución normal"""
        try:
            mean = float(np.mean(data))
            std = float(np.std(data))
            
            shapiro_test = stats.shapiro(data)
            
            result = {
                "mean": mean,
                "std_dev": std,
                "shapiro_test": {
                    "statistic": float(shapiro_test.statistic),
                    "p_value": float(shapiro_test.pvalue),
                    "is_normal": bool(shapiro_test.pvalue > 0.05)
                },
                "pdf": {
                    "x": np.linspace(min(data), max(data), 100).tolist(),
                    "y": stats.norm.pdf(
                        np.linspace(min(data), max(data), 100),
                        loc=mean, scale=std
                    ).tolist()
                }
            }
            
            return ProbabilityAnalyzer._convert_to_native(result)
        except Exception as e:
            logger.error(f"Error en análisis normal: {str(e)}")
            raise

    @staticmethod
    def calculate_advanced_stats(data):
        """Calcula estadísticas avanzadas para un conjunto de datos"""
        if not data or len(data) == 0:
            return {}
        
        series = pd.Series(data)
        stats = {
            "mean": float(series.mean()),
            "median": float(series.median()),
            "mode": [float(x) for x in series.mode().tolist()],
            "skew": float(series.skew()),
            "kurtosis": float(series.kurtosis()),
            "min": float(series.min()),
            "max": float(series.max()),
            "std": float(series.std()),
            "percentiles": {
                "25": float(series.quantile(0.25)),
                "50": float(series.quantile(0.5)),
                "75": float(series.quantile(0.75))
            }
        }
        
        freq, bins = np.histogram(data, bins=10)
        stats["relative_frequency"] = {
            "bins": bins.tolist(),
            "counts": (freq / len(data)).tolist()
        }
        
        return ProbabilityAnalyzer._convert_to_native(stats)