import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def obtener_sesion() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
