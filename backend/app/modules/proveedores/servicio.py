"""Casos de uso. Las tareas asíncronas y otros módulos llaman solo a este servicio."""
from datetime import datetime, timezone
from typing import Protocol
import re

from sqlalchemy.orm import Session

from app.modules.ingredientes.servicio import obtener_ingredientes
from app.integrations.proveedores.telegram import ClienteTelegram, ErrorTelegram

from .esquemas import (OfertaCrear, OfertaPreferidaCompras, ProveedorCrear,
                       VerificacionDestino, ProveedorSalida)
from .modelos import OfertaIngrediente, Proveedor
from .repositorio import RepositorioProveedores


class ErrorDominio(Exception):
    pass


class NoEncontrado(ErrorDominio):
    pass


class Conflicto(ErrorDominio):
    pass


class AdaptadorTelegram(Protocol):
    """Implementado en la capa de integración. Nunca devuelve ni registra la credencial."""
    def verificar_chat(self, chat_id: str) -> bool: ...
    @property
    def huella(self) -> str | None: ...


class ServicioProveedores:
    def __init__(self, db: Session, telegram: AdaptadorTelegram | None = None):
        self.repo = RepositorioProveedores(db)
        self.db = db
        try:
            self.telegram = telegram if telegram is not None else ClienteTelegram.desde_configuracion()
        except ErrorTelegram:
            self.telegram = None

    # --- Proveedores ---
    def crear_proveedor(self, datos: ProveedorCrear) -> Proveedor:
        if self.repo.proveedor_por_codigo(datos.codigo):
            raise Conflicto(f"Ya existe un proveedor con código {datos.codigo}")
        p = Proveedor(**datos.model_dump())
        self.repo.guardar(p)
        self.db.flush()
        return p

    def _proveedor(self, proveedor_id: int, bloquear: bool = False) -> Proveedor:
        p = self.repo.proveedor_por_id(proveedor_id, bloquear)
        if not p:
            raise NoEncontrado("Proveedor no encontrado")
        return p

    def cambiar_estado(self, proveedor_id: int, activo: bool) -> Proveedor:
        p = self._proveedor(proveedor_id)
        p.activo = activo
        self.db.flush()
        return p

    def vincular_chat(self, proveedor_id: int, chat_id: str) -> Proveedor:
        chat_id = chat_id.strip()
        if not re.fullmatch(r"-?[1-9][0-9]{0,18}", chat_id):
            raise Conflicto("Usa el identificador numérico del chat de pruebas, sin @usuario, ceros iniciales ni teléfono.")
        p = self._proveedor(proveedor_id, bloquear=True)
        if p.chat_id_pruebas != chat_id:
            p.chat_id_pruebas = chat_id
            p.destino_verificado = False  # cambiar el destino invalida la verificación
            p.destino_verificado_en = None
            p.destino_credencial_huella = None
        self.db.flush()
        return p

    def verificar_destino(self, proveedor_id: int) -> VerificacionDestino:
        p = self._proveedor(proveedor_id, bloquear=True)
        p.destino_verificado = False
        p.destino_verificado_en = None
        p.destino_credencial_huella = None
        if not p.chat_id_pruebas:
            self.db.flush()
            return VerificacionDestino(verificado=False, codigo="SIN_CHAT", detalle="Sin chat vinculado")
        if self.telegram is None:
            self.db.flush()
            return VerificacionDestino(verificado=False, codigo="CONFIGURACION_ILEGIBLE", detalle="Revisa la configuración protegida de Telegram.")
        try:
            ok = self.telegram.verificar_chat(p.chat_id_pruebas)
        except ErrorTelegram as error:
            self.db.flush()
            return VerificacionDestino(verificado=False, codigo=error.codigo, detalle=str(error))
        except Exception:  # no filtrar detalles que puedan incluir la credencial
            ok = False
        p.destino_verificado = ok
        p.destino_verificado_en = datetime.now(timezone.utc) if ok else None
        p.destino_credencial_huella = self.telegram.huella if ok else None
        self.db.flush()
        return VerificacionDestino(
            verificado=ok, codigo="DESTINO_VERIFICADO" if ok else "DESTINO_NO_VERIFICADO",
            detalle="Acceso al chat de pruebas verificado; no se envió ningún mensaje." if ok else "No se pudo verificar el destino")

    def destino_vigente(self, p: Proveedor) -> bool:
        return bool(p.destino_verificado and p.chat_id_pruebas and self.telegram
                    and self.telegram.huella and p.destino_credencial_huella == self.telegram.huella)

    def salida_proveedor(self, p: Proveedor) -> ProveedorSalida:
        vigente = self.destino_vigente(p)
        return ProveedorSalida.model_validate(p).model_copy(update={
            "destino_verificado": vigente,
            "destino_verificado_en": p.destino_verificado_en if vigente else None})

    def consultar_destino(self, proveedor_id: int, *, bloquear: bool = False) -> ProveedorSalida:
        """Interfaz pública para revisión/aprobación; no expone credencial ni huella."""
        return self.salida_proveedor(self._proveedor(proveedor_id, bloquear=bloquear))

    def puede_enviar(self, proveedor_id: int) -> bool:
        """Destino no verificado bloquea el envío."""
        p = self._proveedor(proveedor_id)
        return bool(p.activo and self.destino_vigente(p))

    # --- Ofertas ---
    def crear_oferta(self, proveedor_id: int, datos: OfertaCrear) -> OfertaIngrediente:
        self._proveedor(proveedor_id)
        ingrediente = obtener_ingredientes(self.db, [datos.ingrediente_id]).get(datos.ingrediente_id)
        if ingrediente is None:
            raise NoEncontrado("Ingrediente no encontrado")
        if not ingrediente.activo:
            raise Conflicto("Ingrediente inactivo")
        d = datos.model_dump()
        preferida = d.pop("preferida")
        oferta = OfertaIngrediente(proveedor_id=proveedor_id, preferida=False, **d)
        self.repo.guardar(oferta)
        if preferida:
            self._marcar_preferida(oferta)
        self.db.flush()
        return oferta

    def marcar_preferida(self, oferta_id: int) -> OfertaIngrediente:
        oferta = self.repo.oferta_por_id(oferta_id)
        if not oferta:
            raise NoEncontrado("Oferta no encontrada")
        if not oferta.activa:
            raise Conflicto("No se puede marcar como preferida una oferta inactiva")
        self._marcar_preferida(oferta)
        self.db.flush()
        return oferta

    def _marcar_preferida(self, oferta: OfertaIngrediente) -> None:
        self.repo.quitar_preferida(oferta.ingrediente_id)
        oferta.preferida = True
        self.db.flush()

    def desactivar_oferta(self, oferta_id: int) -> OfertaIngrediente:
        oferta = self.repo.oferta_por_id(oferta_id)
        if not oferta:
            raise NoEncontrado("Oferta no encontrada")
        oferta.activa = False
        oferta.preferida = False
        self.db.flush()
        return oferta

    # --- Consulta publicada para Compras ---
    def oferta_preferida_para_compras(self, ingrediente_id: int) -> OfertaPreferidaCompras | None:
        o = self.repo.preferida_activa(ingrediente_id)
        if not o:
            return None
        p = o.proveedor
        motivo = None
        if not p.activo:
            motivo = "Proveedor inactivo"
        elif not self.destino_vigente(p):
            motivo = "Destino no verificado"
        return OfertaPreferidaCompras(
            oferta_id=o.id, proveedor_id=p.id, proveedor_codigo=p.codigo,
            proveedor_nombre=p.nombre, proveedor_activo=p.activo,
            chat_id_pruebas=p.chat_id_pruebas, destino_verificado=self.destino_vigente(p),
            ingrediente_id=o.ingrediente_id, unidad_compra=o.unidad_compra,
            factor_conversion=o.factor_conversion, minimo=o.minimo, multiplo=o.multiplo,
            compra_automatica_habilitada=motivo is None, motivo_bloqueo=motivo)
