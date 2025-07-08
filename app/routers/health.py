#fastapi/app/routers/health.py
from fastapi import APIRouter
from app.database.connection import DatabaseConnection

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        # Verificar conexión a la base de datos
        conn = DatabaseConnection.get_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503