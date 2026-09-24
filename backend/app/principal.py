import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.base_datos import engine
from app.modules.autenticacion.rutas import router as autenticacion_router
from app.modules.negocios.rutas import router as negocios_router

app = FastAPI(title="FoodSave API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(autenticacion_router, prefix="/api/v1")
app.include_router(negocios_router, prefix="/api/v1")


@app.get("/salud")
def salud():
    with engine.connect() as conexion:
        conexion.execute(text("SELECT 1"))
    return {"estado": "ok"}
