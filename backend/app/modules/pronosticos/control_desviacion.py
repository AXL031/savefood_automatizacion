"""Control por desviación del pronóstico: lazo de retroalimentación sobre la venta real.

Después de cada evaluación pronóstico-real de una corrida de planificación:

- Mide el WAPE de la corrida con la venta vigente de cada producto.
- Si supera el umbral (consigna) y hay pares suficientes, abre un aviso en la
  bandeja con la evidencia y la acción correctiva sugerida: entrenar una nueva
  versión del modelo con las ventas ya consolidadas por el cierre del día.
- Si una evaluación posterior queda dentro del umbral, cierra sola el aviso
  abierto y deja escrita la medición que lo justifica.

Las corridas BACKTEST no participan: son evaluación histórica, no operación.
El reentrenamiento no se dispara solo: lo aprueba el administrador.
"""
import os
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.operaciones.modelos import AvisoOperacion
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, EvaluacionPronostico

PREFIJO = "desviacion-pronostico:"
TITULO = "Desviación del pronóstico: conviene entrenar una nueva versión del modelo"


def umbral_wape() -> float:
    return float(os.getenv("DESVIACION_WAPE_UMBRAL", "35"))


def minimo_pares() -> int:
    return int(os.getenv("DESVIACION_MIN_PARES", "5"))


@dataclass
class Medicion:
    pares: int
    total_real: int
    error_absoluto: int

    @property
    def wape(self) -> float | None:
        return None if self.total_real == 0 else round(100 * self.error_absoluto / self.total_real, 2)


def medir_corrida(sesion: Session, corrida_id: int) -> Medicion:
    """Usa la evaluación más reciente de cada producto (la revisión de venta vigente)."""
    ultimas: dict[int, EvaluacionPronostico] = {}
    for fila in sesion.scalars(select(EvaluacionPronostico).where(EvaluacionPronostico.corrida_id == corrida_id)
                               .order_by(EvaluacionPronostico.revision_venta_id)):
        ultimas[fila.producto_id] = fila
    return Medicion(len(ultimas), sum(f.unidades_reales for f in ultimas.values()),
                    sum(f.error_absoluto for f in ultimas.values()))


def _abiertos(sesion: Session) -> list[AvisoOperacion]:
    return list(sesion.scalars(select(AvisoOperacion).where(
        AvisoOperacion.clave.like(f"{PREFIJO}%"), AvisoOperacion.resolucion.is_(None)).order_by(AvisoOperacion.id)))


def controlar_desviacion(sesion: Session, corrida_id: int) -> dict:
    """Compara la medición con la consigna y abre o cierra el aviso; no hace commit."""
    corrida = sesion.get(CorridaPronostico, corrida_id)
    if corrida is None or corrida.tipo == "BACKTEST":
        return {"control": "NO_APLICA"}
    medicion, umbral = medir_corrida(sesion, corrida_id), umbral_wape()
    wape = medicion.wape
    base = {"corrida_id": corrida.id, "fecha_objetivo": corrida.fecha_objetivo.isoformat(),
            "pares": medicion.pares, "wape": wape, "umbral": umbral}
    if wape is None or medicion.pares < minimo_pares():
        return {"control": "DATOS_INSUFICIENTES", **base}

    modelo = sesion.get(ArtefactoModelo, corrida.modelo_id)
    abiertos = _abiertos(sesion)
    if wape > umbral:
        if abiertos:
            # Un solo aviso abierto: se actualiza con la última medición, sin repetir la alerta.
            aviso = abiertos[0]
            aviso.datos = {**aviso.datos, "ultima_corrida_id": corrida.id, "ultimo_wape": wape,
                           "desviaciones_consecutivas": int(aviso.datos.get("desviaciones_consecutivas", 1)) + 1}
            sesion.flush()
            return {"control": "DESVIACION", "aviso_id": aviso.id, "nuevo_aviso": False, **base}
        from app.modules.operaciones.servicio import aviso as crear_aviso
        aviso = crear_aviso(sesion, f"{PREFIJO}corrida:{corrida.id}", TITULO, {
            "accion": "REENTRENAR", "modelo_id": modelo.id, "version_modelo": modelo.version_modelo,
            "fecha_corte_entrenamiento": modelo.fecha_corte_entrenamiento.isoformat(),
            "desviaciones_consecutivas": 1, **base,
            "descripcion": (f"El pronóstico del {corrida.fecha_objetivo.isoformat()} (corrida #{corrida.id}, modelo "
                            f"{modelo.version_modelo}) tuvo un WAPE de {wape:.2f} %, por encima del umbral de "
                            f"{umbral:.0f} %, con {medicion.pares} productos evaluados. Entrena una nueva versión para "
                            f"incorporar las ventas cerradas después del {modelo.fecha_corte_entrenamiento.isoformat()} "
                            "y elígela en la próxima programación."),
        })
        return {"control": "DESVIACION", "aviso_id": aviso.id, "nuevo_aviso": True, **base}

    resueltos = []
    for aviso in abiertos:
        if corrida.fecha_objetivo.isoformat() < aviso.datos.get("fecha_objetivo", ""):
            continue  # Una fecha anterior a la desviación no demuestra la corrección.
        aviso.resolucion = (f"Resuelto automáticamente: el pronóstico del {corrida.fecha_objetivo.isoformat()} "
                            f"(corrida #{corrida.id}, modelo {modelo.version_modelo}) volvió a un WAPE de {wape:.2f} %, "
                            f"dentro del umbral de {umbral:.0f} %, con {medicion.pares} productos evaluados.")
        aviso.datos = {**aviso.datos, "resuelto_con_corrida_id": corrida.id, "resuelto_con_modelo_id": modelo.id,
                       "wape_resolucion": wape}
        resueltos.append(aviso.id)
    sesion.flush()
    return {"control": "DENTRO_UMBRAL", "avisos_resueltos": resueltos, **base}
