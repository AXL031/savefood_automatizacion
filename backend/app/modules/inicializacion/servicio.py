"""Asistente de primera carga y estado durable de la inicialización.

La vista previa no toca la base. La confirmación escribe todo en una sola
transacción: si falla el stock o una receta, no queda ni catálogo ni ventas.

Mientras Max (recetas) y Vera (apertura de lotes) no entreguen sus servicios, la
carga persiste lo que pertenece a Edu y deja la instalación en `PENDIENTE` con
constancia de qué falta, en lugar de declararla inicializada.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.inicializacion import lectores
from app.modules.inicializacion.adaptador_bakery import (
    ResumenAdaptacion,
    adaptar_csv_bakery,
    es_csv_bakery,
)
from app.modules.inicializacion.modelos import (
    ESTADO_DATOS_CARGADOS,
    ESTADO_ENTRENANDO,
    ESTADO_FALLIDA,
    ESTADO_MODELO_LISTO,
    ESTADO_PENDIENTE,
    FILA_UNICA,
    ConfiguracionInicial,
)
from app.modules.inicializacion.puertos import ServicioInventario, ServicioRecetas
from app.modules.inicializacion.validacion import ResultadoValidacion, validar_entrega
from app.modules.productos.servicio import EntradaCatalogo, registrar_catalogo
from app.modules.ventas.servicio import registrar_ventas_diarias

def _ruta_lista_curada() -> Path:
    """Encuentra el catálogo tanto en el repositorio como dentro de Docker."""
    nombre = Path("foodsave-ml/lista_productos_precios_limpia.md")
    for carpeta in Path(__file__).resolve().parents:
        candidata = carpeta / nombre
        if candidata.is_file():
            return candidata
    return Path(__file__).resolve().parents[3] / nombre


LISTA_CURADA = _ruta_lista_curada()


@dataclass
class VistaPrevia:
    """Lo que se guardaría si la persona confirma, y lo que está mal."""

    resultado: ResultadoValidacion
    huella_ventas: str
    huella_catalogo: str
    huella_solicitud: str
    resumen_bakery: ResumenAdaptacion | None = None


@dataclass
class InformeCarga:
    """Resultado de una confirmación, con lo pendiente de otros dominios."""

    estado: str
    productos: int
    ventas_diarias: int
    importacion_id: int
    ingredientes: int = 0
    recetas: int = 0
    movimientos_apertura: int = 0
    pendiente_de: list[str] = field(default_factory=list)
    ya_estaba_cargada: bool = False


def skus_curados() -> set[str] | None:
    """SKU válidos del dataset bakery, o `None` si la lista no está disponible."""
    if not LISTA_CURADA.exists():
        return None
    from app.modules.productos.servicio import leer_nombres_bakery

    return set(leer_nombres_bakery(LISTA_CURADA))


def leer_estado(sesion: Session) -> ConfiguracionInicial:
    """Devuelve la fila única, creándola en `PENDIENTE` si la migración no la dejó."""
    estado = sesion.get(ConfiguracionInicial, FILA_UNICA)
    if estado is None:
        estado = ConfiguracionInicial(id=FILA_UNICA, estado=ESTADO_PENDIENTE)
        sesion.add(estado)
        sesion.flush()
    return estado


def _hojas_de_la_entrega(
    archivos: dict[str, bytes], skus_permitidos: set[str] | None
) -> tuple[dict[str, lectores.Hoja], ResumenAdaptacion | None]:
    """Arma las cinco hojas, adaptando el CSV de tickets cuando es el del piloto."""
    nombres = {nombre.strip().lower(): nombre for nombre in archivos}
    clave_ventas = nombres.get("ventas.csv")

    if clave_ventas is not None and es_csv_bakery(archivos[clave_ventas]):
        hoja_ventas, resumen = adaptar_csv_bakery(
            "ventas.csv", archivos[clave_ventas], skus_permitidos
        )
        faltantes = [f"{hoja}.csv" for hoja in lectores.HOJAS_CATALOGO if f"{hoja}.csv" not in nombres]
        if faltantes:
            raise ErrorAPI(
                422,
                "ENTREGA_INCOMPLETA",
                "Con el CSV de tickets faltan los archivos de catálogo: " + ", ".join(faltantes) + ".",
            )
        hojas = {
            hoja: lectores.leer_csv(hoja, f"{hoja}.csv", archivos[nombres[f"{hoja}.csv"]])
            for hoja in lectores.HOJAS_CATALOGO
        }
        hojas["ventas"] = hoja_ventas
        return hojas, resumen

    return lectores.leer_entrega(archivos), None


def preparar_vista_previa(
    archivos: dict[str, bytes],
    fecha_objetivo_demo: date,
    fecha_referencia_stock: date,
    skus_permitidos: set[str] | None = None,
) -> VistaPrevia:
    """Lee, valida y resume la entrega. No escribe nada."""
    hojas, resumen = _hojas_de_la_entrega(archivos, skus_permitidos)
    resultado = validar_entrega(hojas, fecha_objetivo_demo, fecha_referencia_stock, skus_permitidos)
    huella_ventas, huella_catalogo = lectores.huellas_entrega(archivos)
    return VistaPrevia(
        resultado=resultado,
        huella_ventas=huella_ventas,
        huella_catalogo=huella_catalogo,
        huella_solicitud=lectores.huella_solicitud(
            huella_ventas, huella_catalogo, fecha_objetivo_demo, fecha_referencia_stock
        ),
        resumen_bakery=resumen,
    )


def confirmar_carga(
    sesion: Session,
    archivos: dict[str, bytes],
    fecha_objetivo_demo: date,
    fecha_referencia_stock: date,
    clave_importacion: str,
    skus_permitidos: set[str] | None = None,
    puerto_recetas: ServicioRecetas | None = None,
    puerto_inventario: ServicioInventario | None = None,
) -> InformeCarga:
    """Valida y persiste la primera carga en la sesión recibida, sin hacer commit.

    El llamador confirma o revierte. Repetir la misma solicitud sobre una
    instalación ya cargada devuelve el resultado anterior en lugar de duplicar.
    """
    estado = leer_estado(sesion)
    vista = preparar_vista_previa(
        archivos, fecha_objetivo_demo, fecha_referencia_stock, skus_permitidos
    )

    if estado.huella_solicitud == vista.huella_solicitud and estado.estado != ESTADO_PENDIENTE:
        return InformeCarga(
            estado=estado.estado,
            productos=0,
            ventas_diarias=0,
            importacion_id=0,
            ya_estaba_cargada=True,
        )
    if estado.estado in (ESTADO_DATOS_CARGADOS, ESTADO_ENTRENANDO, ESTADO_MODELO_LISTO):
        raise ErrorAPI(
            409,
            "YA_INICIALIZADA",
            "La instalación ya tiene una primera carga aceptada. Requiere reinicialización explícita.",
        )
    if not vista.resultado.aceptable:
        raise ErrorAPI(
            422,
            "CARGA_INVALIDA",
            f"La entrega tiene {vista.resultado.total_errores} problemas; no se guardó nada.",
        )

    entrada = vista.resultado.entrada
    producto_por_codigo = registrar_catalogo(
        sesion,
        [
            EntradaCatalogo(
                codigo=fila.codigo,
                nombre=fila.nombre,
                sku_externo=fila.sku_externo,
                demostrar=fila.demostrar,
            )
            for fila in entrada.productos
        ],
    )

    sku_a_id = {fila.sku_externo: producto_por_codigo[fila.codigo] for fila in entrada.productos}
    diarios = {
        (sku_a_id[venta.sku_externo], venta.fecha_local): venta.unidades_vendidas
        for venta in entrada.ventas
    }
    resultado_ventas = registrar_ventas_diarias(
        sesion,
        diarios,
        clave_importacion=clave_importacion,
        huella_contenido=vista.huella_ventas,
        filas_aceptadas=len(entrada.ventas),
        motivo="Primera carga",
    )

    pendiente: list[str] = []
    ingredientes = recetas = movimientos = 0
    ingrediente_por_codigo: dict[str, int] = {}

    if puerto_recetas is not None:
        ingrediente_por_codigo = puerto_recetas.registrar_ingredientes(sesion, entrada.ingredientes)
        ingredientes = len(ingrediente_por_codigo)
        recetas = puerto_recetas.registrar_recetas(
            sesion, entrada.recetas, producto_por_codigo, ingrediente_por_codigo
        )
    else:
        pendiente.append("ingredientes y recetas (M01, Max Rojas)")

    if puerto_inventario is not None:
        movimientos = puerto_inventario.registrar_apertura(
            sesion,
            entrada.stock,
            producto_por_codigo,
            ingrediente_por_codigo,
            efectivo_en_demo=fecha_referencia_stock,
            clave_operacion_base=f"apertura-{vista.huella_solicitud[:16]}",
        )
    else:
        pendiente.append("apertura de lotes (V01, Leonardo Vera)")

    ahora = datetime.now(timezone.utc)
    completa = not pendiente
    estado.estado = ESTADO_DATOS_CARGADOS if completa else ESTADO_PENDIENTE
    estado.huella_ventas = vista.huella_ventas
    estado.huella_catalogo = vista.huella_catalogo
    estado.huella_solicitud = vista.huella_solicitud
    estado.fecha_objetivo_demo = fecha_objetivo_demo
    estado.fecha_referencia_stock = fecha_referencia_stock
    estado.iniciada_en = estado.iniciada_en or ahora
    estado.completada_en = ahora if completa else None
    estado.mensaje_error = None if completa else "Falta la entrega de: " + "; ".join(pendiente)
    estado.actualizado_en = ahora
    sesion.flush()

    return InformeCarga(
        estado=estado.estado,
        productos=len(producto_por_codigo),
        ventas_diarias=resultado_ventas.ventas_diarias,
        importacion_id=resultado_ventas.importacion_id,
        ingredientes=ingredientes,
        recetas=recetas,
        movimientos_apertura=movimientos,
        pendiente_de=pendiente,
    )


def marcar_entrenando(sesion: Session) -> ConfiguracionInicial:
    """Transición para Kevin/Axel antes de entrenar."""
    estado = leer_estado(sesion)
    if estado.estado not in (ESTADO_DATOS_CARGADOS, ESTADO_FALLIDA):
        raise ErrorAPI(
            409,
            "TRANSICION_INVALIDA",
            f"No se puede entrenar desde el estado {estado.estado}.",
        )
    estado.estado = ESTADO_ENTRENANDO
    estado.mensaje_error = None
    estado.actualizado_en = datetime.now(timezone.utc)
    sesion.flush()
    return estado


def marcar_modelo_listo(sesion: Session) -> ConfiguracionInicial:
    estado = leer_estado(sesion)
    if estado.estado != ESTADO_ENTRENANDO:
        raise ErrorAPI(409, "TRANSICION_INVALIDA", "Solo se pasa a MODELO_LISTO desde ENTRENANDO.")
    ahora = datetime.now(timezone.utc)
    estado.estado = ESTADO_MODELO_LISTO
    estado.mensaje_error = None
    estado.completada_en = estado.completada_en or ahora
    estado.actualizado_en = ahora
    sesion.flush()
    return estado


def marcar_fallo_entrenamiento(sesion: Session, mensaje: str) -> ConfiguracionInicial:
    """Un fallo de entrenamiento vuelve a `DATOS_CARGADOS`: no se recargan datos."""
    estado = leer_estado(sesion)
    if estado.estado != ESTADO_ENTRENANDO:
        raise ErrorAPI(409, "TRANSICION_INVALIDA", "Solo se registra el fallo desde ENTRENANDO.")
    estado.estado = ESTADO_DATOS_CARGADOS
    estado.mensaje_error = mensaje[:2000]
    estado.actualizado_en = datetime.now(timezone.utc)
    sesion.flush()
    return estado


def hay_datos_cargados(sesion: Session) -> bool:
    """Frontera de lectura para Kevin y Axel."""
    estado = sesion.scalar(select(ConfiguracionInicial.estado).where(ConfiguracionInicial.id == FILA_UNICA))
    return estado in (ESTADO_DATOS_CARGADOS, ESTADO_ENTRENANDO, ESTADO_MODELO_LISTO)
