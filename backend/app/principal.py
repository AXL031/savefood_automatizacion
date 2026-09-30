import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.base_datos import engine
from app.core.errores import configurar_errores
from app.modules.autenticacion.rutas import router as autenticacion_router
from app.modules.negocios.rutas import router as negocios_router
from app.modules.automatizaciones.rutas import router_programaciones, router_ejecuciones
from app.modules.inicializacion.rutas import router as inicializacion_router
from app.modules.productos.rutas import router as productos_router
from app.modules.pronosticos.rutas import router as pronosticos_router
from app.modules.ventas.rutas import router as ventas_router

app = FastAPI(title="FoodSave API", version="0.1.0")
configurar_errores(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(autenticacion_router, prefix="/api/v1")
app.include_router(negocios_router, prefix="/api/v1")
app.include_router(router_programaciones, prefix="/api/v1")
app.include_router(router_ejecuciones, prefix="/api/v1")
app.include_router(inicializacion_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")
app.include_router(ventas_router, prefix="/api/v1")
app.include_router(pronosticos_router, prefix="/api/v1")


@app.get("/salud")
def salud():
    with engine.connect() as conexion:
        conexion.execute(text("SELECT 1"))
    return {"estado": "ok"}
