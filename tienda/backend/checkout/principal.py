import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .base_datos import preparar
from .errores import configurar_errores
from .rutas_pagos import router
from .rutas_catalogo import router as catalogo_router
from .integracion import router as integracion_router

@asynccontextmanager
async def vida(app):
    preparar()
    yield

app = FastAPI(title="Tienda · Payme preproducción", lifespan=vida)
app.add_middleware(CORSMiddleware,
    allow_origins=[os.getenv("TIENDA_ORIGIN", "http://localhost:3101")],
    allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"],
    allow_credentials=False)
configurar_errores(app)
app.include_router(router, prefix="/api/v1")
app.include_router(catalogo_router, prefix="/api/v1")
app.include_router(integracion_router, prefix="/api/v1")

@app.get("/salud")
def salud():
    return {"estado": "ok", "proyecto": "tienda", "ambiente": "pruebas"}
