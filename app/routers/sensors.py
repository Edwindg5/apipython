#fastapi/app\routers\sensors.py
from fastapi import APIRouter, Depends, HTTPException
import mysql.connector
from app.database import get_db
import numpy as np
import pandas as pd
from scipy import stats

router = APIRouter()

def print_sensor_status(sensor_type, has_data):
    status = "Datos obtenidos" if has_data else "Sin datos"
    color = "\033[92m" if has_data else "\033[91m"  # Verde para datos, rojo para sin datos
    reset = "\033[0m"
    print(f"{color}• {sensor_type}: {status}{reset}")

@router.get("/sensors-data")
def get_sensors_data(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        print("\n🔍 Buscando datos de sensores...")
        cursor = db.cursor(dictionary=True)
        
        # Obtener los últimos datos de cada sensor
        query = """
        SELECT sr.*, s.type, s.name 
        FROM sensor_readings sr
        JOIN sensors s ON sr.sensor_id = s.id
        WHERE sr.id IN (
            SELECT MAX(id) 
            FROM sensor_readings 
            GROUP BY sensor_id
        )
        ORDER BY s.id
        """
        
        cursor.execute(query)
        sensors_data = cursor.fetchall()
        
        if not sensors_data:
            print("⚠️ No se encontraron sensores en la base de datos")
            return {"message": "No se encontraron datos de sensores"}
        
        # Verificar datos por tipo de sensor
        sensor_types = {'DHT22': False, 'BME280': False, 'INA219': False, 'DS18B20': False}
        
        # Imprimir en consola
        print("\n📊 === Datos de Sensores ===")
        for sensor in sensors_data:
            sensor_type = sensor['type']
            sensor_types[sensor_type] = True
            
            print(f"\n📡 Sensor ID: {sensor['sensor_id']}")
            print(f"🔧 Tipo: {sensor_type}")
            print(f"🏷️ Nombre: {sensor['name']}")
            
            if sensor_type == 'DHT22':
                print(f"🌡️ Temperatura: {sensor['temperature'] or 'N/A'}°C")
                print(f"💧 Humedad: {sensor['humidity'] or 'N/A'}%")
            elif sensor_type == 'BME280':
                print(f"🌡️ Temperatura: {sensor['temperature'] or 'N/A'}°C")
                print(f"💧 Humedad: {sensor['humidity'] or 'N/A'}%")
                print(f"📊 Presión: {sensor['pressure'] or 'N/A'} hPa")
            elif sensor_type == 'INA219':
                print(f"⚡ Voltaje: {sensor['voltage'] or 'N/A'} V")
                print(f"🔌 Corriente: {sensor['current'] or 'N/A'} A")
            elif sensor_type == 'DS18B20':
                print(f"🌡️ Temperatura: {sensor['temperature'] or 'N/A'}°C")
            
            print(f"⏰ Fecha: {sensor['recorded_at']}")
        
        # Mostrar resumen por tipo de sensor
        print("\n📋 Resumen de sensores:")
        for sensor_type, has_data in sensor_types.items():
            print_sensor_status(sensor_type, has_data)
        
        return {"sensors": sensors_data}
        
    except Exception as e:
        print(f"❌ Error al obtener datos de sensores: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener datos de sensores")
    finally:
        if db.is_connected():
            cursor.close()
            db.close()
            print("\n🔌 Conexión con la base de datos cerrada")
            
            
@router.get("/pressure-stats")
def get_pressure_stats(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        print("\n📊 Calculando estadísticas de presión...")
        cursor = db.cursor(dictionary=True)
        
        # Obtener todos los datos de presión del BME280
        query = """
        SELECT sr.pressure, sr.recorded_at
        FROM sensor_readings sr
        JOIN sensors s ON sr.sensor_id = s.id
        WHERE s.type = 'BME280' AND sr.pressure IS NOT NULL
        ORDER BY sr.recorded_at
        """
        
        cursor.execute(query)
        pressure_data = cursor.fetchall()
        
        if not pressure_data:
            print("⚠️ No se encontraron datos de presión")
            return {"message": "No se encontraron datos de presión"}
        
        # Convertir a DataFrame de pandas
        df = pd.DataFrame(pressure_data)
        pressures = df['pressure'].values
        
        # Calcular estadísticas
        stats_dict = {
            "Media": float(np.mean(pressures)),
            "Mediana": float(np.median(pressures)),
            "Mínimo": float(np.min(pressures)),
            "Máximo": float(np.max(pressures)),
            "Rango": float(np.ptp(pressures)),
            "Desviación Estándar": float(np.std(pressures)),
            "Cantidad de muestras": len(pressures)
        }
        
        # Calcular moda de manera segura
        try:
            mode_result = stats.mode(pressures)
            stats_dict["Moda"] = float(mode_result.mode[0] if hasattr(mode_result, 'mode') else mode_result[0][0])
        except:
            stats_dict["Moda"] = "No disponible"
        
        # Calcular sesgo de manera segura
        try:
            stats_dict["Sesgo"] = float(stats.skew(pressures))
        except:
            stats_dict["Sesgo"] = "No disponible"
        
        # Tabla de frecuencias (convertir los bins a strings)
        freq_table = pd.cut(pressures, bins=5).value_counts().sort_index()
        freq_table_dict = {str(interval): int(count) for interval, count in freq_table.items()}
        
        # Mostrar resultados en consola
        print("\n=== Estadísticas de Presión ===")
        print(f"\n📌 Datos Básicos:")
        for key, value in stats_dict.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        
        print("\n📊 Tabla de Frecuencias:")
        print(pd.Series(freq_table_dict).to_string())
        
        print(f"\n📅 Primera medición: {df['recorded_at'].iloc[0]}")
        print(f"📅 Última medición: {df['recorded_at'].iloc[-1]}")
        
        return {
            "stats": stats_dict,
            "frequency_table": freq_table_dict,  # Usamos el diccionario convertido
            "first_reading": str(df['recorded_at'].iloc[0]),
            "last_reading": str(df['recorded_at'].iloc[-1])
        }
        
    except Exception as e:
        print(f"❌ Error al calcular estadísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db.is_connected():
            cursor.close()
            db.close()
            
@router.get("/humidity-stats")
def get_humidity_stats(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    try:
        print("\n💧 Calculando estadísticas de humedad...")
        cursor = db.cursor(dictionary=True)
        
        # Obtener todos los datos de humedad
        query = """
        SELECT sr.humidity, sr.recorded_at, s.type
        FROM sensor_readings sr
        JOIN sensors s ON sr.sensor_id = s.id
        WHERE s.type IN ('DHT22', 'BME280') AND sr.humidity IS NOT NULL
        ORDER BY sr.recorded_at
        """
        
        cursor.execute(query)
        humidity_data = cursor.fetchall()
        
        if not humidity_data:
            print("⚠️ No se encontraron datos de humedad")
            return {"message": "No se encontraron datos de humedad"}
        
        df = pd.DataFrame(humidity_data)
        humidities = df['humidity'].values
        
        stats_dict = {
            "Media": float(np.mean(humidities)),
            "Mediana": float(np.median(humidities)),
            "Mínimo": float(np.min(humidities)),
            "Máximo": float(np.max(humidities)),
            "Rango": float(np.ptp(humidities)),
            "Desviación Estándar": float(np.std(humidities)),
            "Cantidad de muestras": len(humidities)
        }
        
        # Cálculo robusto de moda
        try:
            unique_values, counts = np.unique(humidities, return_counts=True)
            max_count = np.max(counts)
            modes = unique_values[counts == max_count]
            
            if len(modes) == 1:
                stats_dict["Moda"] = float(modes[0])
            elif len(modes) > 1:
                stats_dict["Moda"] = f"Múltiples modas: {', '.join(map(str, modes))}"
            else:
                stats_dict["Moda"] = "No disponible"
        except Exception as e:
            print(f"⚠️ Error calculando moda: {str(e)}")
            stats_dict["Moda"] = "No disponible"
        
        # Resto del código permanece igual...
        sensor_stats = {}
        for sensor_type in ['DHT22', 'BME280']:
            sensor_data = df[df['type'] == sensor_type]['humidity']
            if not sensor_data.empty:
                sensor_stats[sensor_type] = {
                    "Media": float(np.mean(sensor_data)),
                    "Muestras": len(sensor_data)
                }
        
        freq_table = pd.cut(humidities, bins=5).value_counts().sort_index()
        freq_table_dict = {str(interval): int(count) for interval, count in freq_table.items()}
        
        print("\n=== Estadísticas de Humedad ===")
        print(f"\n📌 Datos Básicos:")
        for key, value in stats_dict.items():
            print(f"{key}: {value}")
        
        return {
            "stats": stats_dict,
            "sensor_stats": sensor_stats,
            "frequency_table": freq_table_dict,
            "first_reading": str(df['recorded_at'].iloc[0]),
            "last_reading": str(df['recorded_at'].iloc[-1])
        }
        
    except Exception as e:
        print(f"❌ Error al calcular estadísticas de humedad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db.is_connected():
            cursor.close()
            db.close()