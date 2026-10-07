"""Persistencia."""
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .modelos import OfertaIngrediente, Proveedor


class RepositorioProveedores:
    def __init__(self, db: Session):
        self.db = db

    def proveedor_por_id(self, proveedor_id: int, bloquear: bool = False) -> Proveedor | None:
        if bloquear:
            return self.db.scalar(select(Proveedor).where(Proveedor.id == proveedor_id)
                                  .with_for_update().execution_options(populate_existing=True))
        return self.db.get(Proveedor, proveedor_id)

    def proveedor_por_codigo(self, codigo: str) -> Proveedor | None:
        return self.db.scalar(select(Proveedor).where(Proveedor.codigo == codigo))

    def listar_proveedores(self) -> list[Proveedor]:
        return list(self.db.scalars(select(Proveedor).order_by(Proveedor.nombre)))

    def guardar(self, obj):
        self.db.add(obj)
        self.db.flush()
        return obj

    def oferta_por_id(self, oferta_id: int) -> OfertaIngrediente | None:
        return self.db.get(OfertaIngrediente, oferta_id)

    def ofertas_de_proveedor(self, proveedor_id: int) -> list[OfertaIngrediente]:
        return list(self.db.scalars(
            select(OfertaIngrediente).where(OfertaIngrediente.proveedor_id == proveedor_id)))

    def preferida_activa(self, ingrediente_id: int) -> OfertaIngrediente | None:
        return self.db.scalar(select(OfertaIngrediente).where(
            OfertaIngrediente.ingrediente_id == ingrediente_id,
            OfertaIngrediente.preferida.is_(True),
            OfertaIngrediente.activa.is_(True)))

    def quitar_preferida(self, ingrediente_id: int) -> None:
        self.db.execute(update(OfertaIngrediente)
                        .where(OfertaIngrediente.ingrediente_id == ingrediente_id)
                        .values(preferida=False))
        self.db.flush()
