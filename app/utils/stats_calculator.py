#fastapi/app/utils/stats_calculator.py
import numpy as np
from scipy import stats
import math
import logging

logger = logging.getLogger(__name__)

def _is_valid_number(value):
    """Verifica si un valor es un número válido (no NaN, no infinito)"""
    return not (math.isnan(value) or math.isinf(value))

def _safe_float_convert(value, default=None):
    """Convierte un valor a float de manera segura, manejando NaN e infinitos"""
    try:
        if isinstance(value, (np.generic, np.ndarray)):
            value = float(value)
        
        if _is_valid_number(value):
            return float(value)
        else:
            return default
    except (ValueError, TypeError, OverflowError):
        return default

def calculate_stats(values):
    """
    Calcula estadísticas básicas de manera robusta, manejando casos edge
    y asegurando compatibilidad JSON
    """
    if not values or len(values) == 0:
        return {
            "Mean": None,
            "Median": None,
            "Min": None,
            "Max": None,
            "Range": None,
            "STD": None,
            "Sample Size": 0,
            "Mode": None,
            "Skewness": None
        }
    
    try:
        np_values = np.array(values, dtype=float)
        valid_values = np_values[np.isfinite(np_values)]
        
        if len(valid_values) == 0:
            logger.warning("Todos los valores son NaN o infinitos")
            return {
                "Mean": None,
                "Median": None,
                "Min": None,
                "Max": None,
                "Range": None,
                "STD": None,
                "Sample Size": len(values),
                "Mode": None,
                "Skewness": None
            }
    except Exception as e:
        logger.error(f"Error convirtiendo valores a numpy array: {str(e)}")
        return {
            "Mean": None,
            "Median": None,
            "Min": None,
            "Max": None,
            "Range": None,
            "STD": None,
            "Sample Size": len(values) if values else 0,
            "Mode": None,
            "Skewness": None
        }

    stats_dict = {
        "Sample Size": len(values)
    }

    try:
        stats_dict["Mean"] = _safe_float_convert(np.mean(valid_values))
        stats_dict["Median"] = _safe_float_convert(np.median(valid_values))
        stats_dict["Min"] = _safe_float_convert(np.min(valid_values))
        stats_dict["Max"] = _safe_float_convert(np.max(valid_values))
        
        if stats_dict["Max"] is not None and stats_dict["Min"] is not None:
            stats_dict["Range"] = stats_dict["Max"] - stats_dict["Min"]
        else:
            stats_dict["Range"] = None

        if len(valid_values) > 1:
            std_val = np.std(valid_values, ddof=1)
            stats_dict["STD"] = _safe_float_convert(std_val)
        else:
            stats_dict["STD"] = None
    except Exception as e:
        logger.error(f"Error calculando estadísticas básicas: {str(e)}")
        stats_dict.update({
            "Mean": None,
            "Median": None,
            "Min": None,
            "Max": None,
            "Range": None,
            "STD": None
        })

    try:
        if len(valid_values) > 0:
            unique_values, counts = np.unique(valid_values, return_counts=True)
            max_count = np.max(counts)
            modes = unique_values[counts == max_count]
            
            if len(modes) == 1:
                stats_dict["Mode"] = _safe_float_convert(modes[0])
            elif len(modes) > 1 and len(modes) <= 5:
                mode_list = [_safe_float_convert(m) for m in modes[:5]]
                mode_list = [m for m in mode_list if m is not None]
                if mode_list:
                    stats_dict["Mode"] = f"Multiple modes: {', '.join(map(str, mode_list))}"
                else:
                    stats_dict["Mode"] = None
            else:
                stats_dict["Mode"] = "Uniform distribution"
        else:
            stats_dict["Mode"] = None
    except Exception as e:
        logger.error(f"Error calculando moda: {str(e)}")
        stats_dict["Mode"] = None

    try:
        if len(valid_values) > 2:
            if stats_dict["STD"] is not None and stats_dict["STD"] > 1e-10:
                skew_val = stats.skew(valid_values)
                stats_dict["Skewness"] = _safe_float_convert(skew_val)
            else:
                logger.warning("STD muy pequeña o cero, sesgo no calculable")
                stats_dict["Skewness"] = None
        else:
            stats_dict["Skewness"] = None
    except Exception as e:
        logger.warning(f"Error calculando sesgo: {str(e)}")
        stats_dict["Skewness"] = None

    return stats_dict
