from fastapi import APIRouter, Depends, HTTPException
import mysql.connector
from app.database import get_db

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