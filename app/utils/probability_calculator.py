#probability_calculator.py
import numpy as np
from scipy import stats
import pandas as pd
import logging
import math

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
    def _clean_for_json(data):
        """Reemplaza NaN o infinitos por None para compatibilidad JSON"""
        if isinstance(data, float):
            return None if (math.isnan(data) or math.isinf(data)) else data
        elif isinstance(data, (np.floating, np.integer)):
            val = float(data)
            return None if (math.isnan(val) or math.isinf(val)) else val
        elif isinstance(data, dict):
            return {k: ProbabilityAnalyzer._clean_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [ProbabilityAnalyzer._clean_for_json(v) for v in data]
        else:
            return data

    @staticmethod
    def _validate_data(data, min_length=1):
        """Valida y limpia los datos de entrada"""
        if data is None or len(data) == 0:
            raise ValueError("Datos vacíos o None")
        
        # Convertir a numpy array y filtrar valores válidos
        np_data = np.array(data, dtype=float)
        valid_data = np_data[np.isfinite(np_data)]
        
        if len(valid_data) < min_length:
            raise ValueError(f"Insuficientes datos válidos: {len(valid_data)} < {min_length}")
        
        return valid_data

    @staticmethod
    def calculate_joint_probability(data1, data2, bin_size=10):
        """
        Calcula la probabilidad conjunta de dos variables continuas
        """
        try:
            # Validar datos
            valid_data1 = ProbabilityAnalyzer._validate_data(data1, min_length=2)
            valid_data2 = ProbabilityAnalyzer._validate_data(data2, min_length=2)
            
            # Asegurar que ambos arrays tengan la misma longitud
            min_len = min(len(valid_data1), len(valid_data2))
            valid_data1 = valid_data1[:min_len]
            valid_data2 = valid_data2[:min_len]
            
            if min_len < 2:
                logger.warning("Datos insuficientes para probabilidad conjunta")
                return {
                    "table": {},
                    "bins1": [],
                    "bins2": [],
                    "message": "Datos insuficientes"
                }

            # Crear bins de manera robusta
            try:
                data1_cut, bins1 = pd.cut(valid_data1, bins=min(bin_size, len(valid_data1)//2 + 1), retbins=True, duplicates='drop')
                data2_cut, bins2 = pd.cut(valid_data2, bins=min(bin_size, len(valid_data2)//2 + 1), retbins=True, duplicates='drop')
            except ValueError as e:
                logger.warning(f"Error creando bins: {str(e)}")
                # Fallback: usar bins únicos basados en valores únicos
                bins1 = np.unique(valid_data1)
                bins2 = np.unique(valid_data2)
                data1_cut = pd.cut(valid_data1, bins=bins1, include_lowest=True, duplicates='drop')
                data2_cut = pd.cut(valid_data2, bins=bins2, include_lowest=True, duplicates='drop')

            data1_str = data1_cut.astype(str)
            data2_str = data2_cut.astype(str)

            contingency_table = pd.crosstab(
                data1_str,
                data2_str,
                normalize=True
            )

            logger.info("Probabilidad conjunta calculada exitosamente")

            result = {
                "table": contingency_table.to_dict(),
                "bins1": bins1.tolist() if hasattr(bins1, 'tolist') else list(bins1),
                "bins2": bins2.tolist() if hasattr(bins2, 'tolist') else list(bins2)
            }

            result = ProbabilityAnalyzer._clean_for_json(result)
            return ProbabilityAnalyzer._convert_to_native(result)

        except Exception as e:
            logger.error(f"Error calculando probabilidad conjunta: {str(e)}")
            return {
                "table": {},
                "bins1": [],
                "bins2": [],
                "error": str(e)
            }

    @staticmethod
    def binomial_analysis(data, success_condition, n_trials=None):
        """
        Realiza análisis binomial sobre datos de sensores
        """
        try:
            valid_data = ProbabilityAnalyzer._validate_data(data, min_length=1)
            
            if n_trials is None:
                n_trials = len(valid_data)

            # Aplicar condición de éxito de manera segura
            try:
                successes = sum(1 for x in valid_data if success_condition(x))
            except Exception as e:
                logger.error(f"Error aplicando condición de éxito: {str(e)}")
                successes = 0

            if n_trials == 0:
                logger.warning("No hay trials para análisis binomial")
                return {
                    "n_trials": 0,
                    "successes": 0,
                    "p": None,
                    "mean": None,
                    "variance": None,
                    "std_dev": None,
                    "pmf": []
                }

            p = successes / n_trials
            mean = n_trials * p
            var = n_trials * p * (1 - p)
            std = np.sqrt(var)

            # Calcular PMF de manera limitada para evitar arrays muy grandes
            max_pmf_points = min(n_trials + 1, 100)
            pmf_values = []
            
            try:
                for k in range(max_pmf_points):
                    pmf_val = stats.binom.pmf(k, n_trials, p)
                    pmf_values.append(float(pmf_val) if np.isfinite(pmf_val) else 0.0)
            except Exception as e:
                logger.warning(f"Error calculando PMF: {str(e)}")
                pmf_values = [0.0] * max_pmf_points

            result = {
                "n_trials": int(n_trials),
                "successes": int(successes),
                "p": float(p),
                "mean": float(mean),
                "variance": float(var),
                "std_dev": float(std),
                "pmf": pmf_values
            }

            result = ProbabilityAnalyzer._clean_for_json(result)
            return ProbabilityAnalyzer._convert_to_native(result)

        except Exception as e:
            logger.error(f"Error en análisis binomial: {str(e)}")
            return {
                "n_trials": 0,
                "successes": 0,
                "p": None,
                "mean": None,
                "variance": None,
                "std_dev": None,
                "pmf": [],
                "error": str(e)
            }

    @staticmethod
    def normal_distribution_analysis(data):
        """Analiza cómo se ajustan los datos a una distribución normal"""
        try:
            valid_data = ProbabilityAnalyzer._validate_data(data, min_length=3)

            mean = float(np.mean(valid_data))
            std = float(np.std(valid_data, ddof=1))

            if std == 0 or not np.isfinite(std):
                logger.warning("Distribución normal no válida: desviación estándar cero o NaN")
                return {
                    "mean": mean,
                    "std_dev": None,
                    "shapiro_test": {
                        "statistic": None,
                        "p_value": None,
                        "is_normal": None
                    },
                    "pdf": {
                        "x": valid_data.tolist(),
                        "y": [1.0/len(valid_data)] * len(valid_data)
                    }
                }

            # Test de normalidad solo si hay suficientes datos
            shapiro_result = {"statistic": None, "p_value": None, "is_normal": None}
            
            if len(valid_data) >= 3 and len(valid_data) <= 5000:  # Shapiro-Wilk tiene límites
                try:
                    shapiro_test = stats.shapiro(valid_data)
                    shapiro_result = {
                        "statistic": float(shapiro_test.statistic),
                        "p_value": float(shapiro_test.pvalue),
                        "is_normal": bool(shapiro_test.pvalue > 0.05)
                    }
                except Exception as e:
                    logger.warning(f"Error en test Shapiro-Wilk: {str(e)}")

            # Generar PDF
            try:
                x_vals = np.linspace(
                    np.min(valid_data) - std, 
                    np.max(valid_data) + std, 
                    min(100, len(valid_data) * 2)
                )
                y_vals = stats.norm.pdf(x_vals, loc=mean, scale=std)
                
                # Filtrar valores inválidos del PDF
                valid_indices = np.isfinite(y_vals)
                x_vals = x_vals[valid_indices]
                y_vals = y_vals[valid_indices]
                
            except Exception as e:
                logger.warning(f"Error generando PDF: {str(e)}")
                x_vals = valid_data
                y_vals = np.ones_like(valid_data) / len(valid_data)

            result = {
                "mean": mean,
                "std_dev": std,
                "shapiro_test": shapiro_result,
                "pdf": {
                    "x": x_vals.tolist(),
                    "y": y_vals.tolist()
                }
            }

            result = ProbabilityAnalyzer._clean_for_json(result)
            return ProbabilityAnalyzer._convert_to_native(result)

        except Exception as e:
            logger.error(f"Error en análisis normal: {str(e)}")
            return {
                "mean": None,
                "std_dev": None,
                "shapiro_test": {
                    "statistic": None,
                    "p_value": None,
                    "is_normal": None
                },
                "pdf": {"x": [], "y": []},
                "error": str(e)
            }

    @staticmethod
    def calculate_advanced_stats(data):
        """Calcula estadísticas avanzadas para un conjunto de datos"""
        if not data or len(data) == 0:
            return {}

        try:
            valid_data = ProbabilityAnalyzer._validate_data(data, min_length=1)
            series = pd.Series(valid_data)
            
            # Calcular estadísticas básicas
            stats_dict = {
                "mean": float(series.mean()),
                "median": float(series.median()),
                "min": float(series.min()),
                "max": float(series.max()),
                "std": float(series.std())
            }

            # Moda (puede ser múltiple)
            try:
                mode_series = series.mode()
                if len(mode_series) > 0:
                    stats_dict["mode"] = [float(x) for x in mode_series.tolist()[:5]]  # Limitar modas
                else:
                    stats_dict["mode"] = []
            except Exception:
                stats_dict["mode"] = []

            # Sesgo y curtosis (requieren más de 2 valores)
            if len(valid_data) > 2:
                try:
                    skew_val = series.skew()
                    stats_dict["skew"] = float(skew_val) if np.isfinite(skew_val) else None
                except Exception:
                    stats_dict["skew"] = None
                    
                try:
                    kurt_val = series.kurtosis()
                    stats_dict["kurtosis"] = float(kurt_val) if np.isfinite(kurt_val) else None
                except Exception:
                    stats_dict["kurtosis"] = None
            else:
                stats_dict["skew"] = None
                stats_dict["kurtosis"] = None

            # Percentiles
            try:
                stats_dict["percentiles"] = {
                    "25": float(series.quantile(0.25)),
                    "50": float(series.quantile(0.5)),
                    "75": float(series.quantile(0.75))
                }
            except Exception:
                stats_dict["percentiles"] = {"25": None, "50": None, "75": None}

            # Frecuencia relativa
            try:
                n_bins = min(10, len(np.unique(valid_data)))
                freq, bins = np.histogram(valid_data, bins=n_bins)
                
                # Asegurar que no hay valores infinitos o NaN
                freq_relative = freq / len(valid_data)
                
                stats_dict["relative_frequency"] = {
                    "bins": [float(b) for b in bins],
                    "counts": [float(f) for f in freq_relative]
                }
            except Exception as e:
                logger.warning(f"Error calculando frecuencia relativa: {str(e)}")
                stats_dict["relative_frequency"] = {"bins": [], "counts": []}

            stats_dict = ProbabilityAnalyzer._clean_for_json(stats_dict)
            return ProbabilityAnalyzer._convert_to_native(stats_dict)

        except Exception as e:
            logger.error(f"Error en cálculo de estadísticas avanzadas: {str(e)}")
            return {"error": str(e)}