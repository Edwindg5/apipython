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
            "Media": None,
            "Mediana": None,
            "Mínimo": None,
            "Máximo": None,
            "Rango": None,
            "Desviación Estándar": None,
            "Cantidad de muestras": 0,
            "Moda": None,
            "Sesgo": None
        }
    
    # Convertir a numpy array para cálculos más robustos
    try:
        np_values = np.array(values, dtype=float)
        # Filtrar valores inválidos (NaN, infinitos)
        valid_values = np_values[np.isfinite(np_values)]
        
        if len(valid_values) == 0:
            logger.warning("Todos los valores son NaN o infinitos")
            return {
                "Media": None,
                "Mediana": None,
                "Mínimo": None,
                "Máximo": None,
                "Rango": None,
                "Desviación Estándar": None,
                "Cantidad de muestras": len(values),
                "Moda": None,
                "Sesgo": None
            }
            
    except Exception as e:
        logger.error(f"Error convirtiendo valores a numpy array: {str(e)}")
        return {
            "Media": None,
            "Mediana": None,
            "Mínimo": None,
            "Máximo": None,
            "Rango": None,
            "Desviación Estándar": None,
            "Cantidad de muestras": len(values) if values else 0,
            "Moda": None,
            "Sesgo": None
        }
    
    # Inicializar diccionario de estadísticas
    stats_dict = {
        "Cantidad de muestras": len(values)
    }
    
    # Calcular estadísticas básicas
    try:
        stats_dict["Media"] = _safe_float_convert(np.mean(valid_values))
        stats_dict["Mediana"] = _safe_float_convert(np.median(valid_values))
        stats_dict["Mínimo"] = _safe_float_convert(np.min(valid_values))
        stats_dict["Máximo"] = _safe_float_convert(np.max(valid_values))
        
        # Rango
        if stats_dict["Máximo"] is not None and stats_dict["Mínimo"] is not None:
            stats_dict["Rango"] = stats_dict["Máximo"] - stats_dict["Mínimo"]
        else:
            stats_dict["Rango"] = None
            
        # Desviación estándar
        if len(valid_values) > 1:
            std_val = np.std(valid_values, ddof=1)  # Usar ddof=1 para muestra
            stats_dict["Desviación Estándar"] = _safe_float_convert(std_val)
        else:
            stats_dict["Desviación Estándar"] = None
            
    except Exception as e:
        logger.error(f"Error calculando estadísticas básicas: {str(e)}")
        stats_dict.update({
            "Media": None,
            "Mediana": None,
            "Mínimo": None,
            "Máximo": None,
            "Rango": None,
            "Desviación Estándar": None
        })
    
    # Calcular moda de manera robusta
    try:
        if len(valid_values) > 0:
            unique_values, counts = np.unique(valid_values, return_counts=True)
            max_count = np.max(counts)
            modes = unique_values[counts == max_count]
            
            if len(modes) == 1:
                stats_dict["Moda"] = _safe_float_convert(modes[0])
            elif len(modes) > 1 and len(modes) <= 5:  # Limitar número de modas mostradas
                mode_list = [_safe_float_convert(m) for m in modes[:5]]
                mode_list = [m for m in mode_list if m is not None]
                if mode_list:
                    stats_dict["Moda"] = f"Múltiples modas: {', '.join(map(str, mode_list))}"
                else:
                    stats_dict["Moda"] = None
            else:
                stats_dict["Moda"] = "Distribución uniforme"
        else:
            stats_dict["Moda"] = None
    except Exception as e:
        logger.error(f"Error calculando moda: {str(e)}")
        stats_dict["Moda"] = None
    
    # Calcular sesgo de manera robusta
    try:
        if len(valid_values) > 2:  # Se necesitan al menos 3 valores para sesgo
            # Verificar si hay variabilidad suficiente
            if stats_dict["Desviación Estándar"] is not None and stats_dict["Desviación Estándar"] > 1e-10:
                skew_val = stats.skew(valid_values)
                stats_dict["Sesgo"] = _safe_float_convert(skew_val)
            else:
                logger.warning("Desviación estándar muy pequeña o cero, sesgo no calculable")
                stats_dict["Sesgo"] = None
        else:
            stats_dict["Sesgo"] = None
    except Exception as e:
        logger.warning(f"Error calculando sesgo: {str(e)}")
        stats_dict["Sesgo"] = None
    
    return stats_dict