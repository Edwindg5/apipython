#fastapi/app\main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db
from app.routers.sensors import router as sensors_router

app = FastAPI()

# Evento para verificar conexión al iniciar
@app.on_event("startup")
async def startup_event():
    # Solo para probar conexión
    try:
        db = get_db()
        db.close()
    except Exception as e:
        print(f"[APP] Error inicial: {e}")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sensors_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "API de Sensores en funcionamiento"}