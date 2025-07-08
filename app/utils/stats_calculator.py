#fastapi/app/utils/stats_calculator.py
import numpy as np
from scipy import stats

def calculate_stats(values):
    stats_dict = {
        "Media": float(np.mean(values)),
        "Mediana": float(np.median(values)),
        "Mínimo": float(np.min(values)),
        "Máximo": float(np.max(values)),
        "Rango": float(np.ptp(values)),
        "Desviación Estándar": float(np.std(values)),
        "Cantidad de muestras": len(values)
    }
    
    try:
        unique_values, counts = np.unique(values, return_counts=True)
        max_count = np.max(counts)
        modes = unique_values[counts == max_count]
        
        if len(modes) == 1:
            stats_dict["Moda"] = float(modes[0])
        elif len(modes) > 1:
            stats_dict["Moda"] = f"Múltiples modas: {', '.join(map(str, modes))}"
        else:
            stats_dict["Moda"] = "No disponible"
    except Exception:
        stats_dict["Moda"] = "No disponible"
    
    try:
        stats_dict["Sesgo"] = float(stats.skew(values))
    except Exception:
        stats_dict["Sesgo"] = "No disponible"
    
    return stats_dict
