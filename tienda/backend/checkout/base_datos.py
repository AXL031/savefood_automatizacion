"""Almacenamiento exclusivo de la tienda; nunca abre la base de FoodSave."""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from .modelos import Base

engine = create_engine(os.getenv("TIENDA_DATABASE_URL", "sqlite:////datos/tienda.db"),
                       connect_args={"check_same_thread": False, "timeout": 15})

@event.listens_for(engine, "connect")
def conectar(dbapi, _):
    dbapi.isolation_level = None
    dbapi.execute("PRAGMA foreign_keys=ON")
    dbapi.execute("PRAGMA journal_mode=WAL")

@event.listens_for(engine, "begin")
def transaccion(conn):
    # SQLite no implementa FOR UPDATE: serializar transacciones evita perder eventos.
    conn.exec_driver_sql("BEGIN IMMEDIATE")

def preparar():
    Base.metadata.create_all(engine)

def obtener_sesion():
    with Session(engine) as sesion:
        yield sesion
