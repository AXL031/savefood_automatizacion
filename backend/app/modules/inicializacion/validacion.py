"""Validación de la primera carga antes de escribir en la base.

Reúne todos los problemas del lote en lugar de detenerse en el primero, para que
la persona corrija una sola vez. Un error rechaza la carga entera.

Reglas que hace cumplir: fila ausente de `ventas` es desconocido y cero explícito
es dato; un SKU de ventas sin fila en `productos` rechaza el lote; las cantidades
usan `Decimal`; `fecha_referencia_stock` es anterior a `fecha_objetivo_demo`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation

from app.modules.inicializacion.lectores import Hoja

UNIDADES_BASE = ("g", "kg", "ml", "l", "unidad")
TIPOS_STOCK = ("producto", "ingrediente")
DECIMALES_INGREDIENTE = 3

# Un archivo mal exportado puede fallar en cientos de miles de filas; se informa
# el total aparte.
MAXIMO_ERRORES = 200


@dataclass(frozen=True)
class ErrorEntrada:

    archivo: str
    campo: str
    mensaje: str
    fila: int | None = None

    def como_detalle(self) -> dict[str, str]:
        ubicacion = f"{self.archivo}:{self.fila}" if self.fila is not None else self.archivo
        return {"campo": f"{ubicacion}/{self.campo}", "mensaje": self.mensaje}


@dataclass(frozen=True)
class FilaProducto:
    codigo: str
    nombre: str
    sku_externo: str
    demostrar: bool


@dataclass(frozen=True)
class FilaIngrediente:
    codigo: str
    nombre: str
    unidad_base: str


@dataclass(frozen=True)
class FilaReceta:
    codigo_producto: str
    codigo_ingrediente: str
    cantidad_por_unidad: Decimal


@dataclass(frozen=True)
class FilaStock:
    tipo: str
    codigo: str
    cantidad: Decimal
    codigo_lote: str | None
    fecha_caducidad: date | None
    fecha_limite_venta: date | None


@dataclass(frozen=True)
class FilaVenta:
    fecha_local: date
    sku_externo: str
    unidades_vendidas: int


@dataclass
class EntradaValidada:
    """Lote aceptado, listo para persistir en una sola transacción."""

    productos: list[FilaProducto] = field(default_factory=list)
    ingredientes: list[FilaIngrediente] = field(default_factory=list)
    recetas: list[FilaReceta] = field(default_factory=list)
    stock: list[FilaStock] = field(default_factory=list)
    ventas: list[FilaVenta] = field(default_factory=list)
    fecha_objetivo_demo: date | None = None
    fecha_referencia_stock: date | None = None

    @property
    def productos_demo(self) -> list[FilaProducto]:
        return [producto for producto in self.productos if producto.demostrar]


@dataclass
class ResultadoValidacion:
    """Vista previa del lote: lo que se guardaría y lo que está mal."""

    entrada: EntradaValidada
    errores: list[ErrorEntrada]
    total_errores: int
    filas_por_hoja: dict[str, int]
    fechas_ventas: tuple[date | None, date | None]
    skus_en_ventas: int

    @property
    def aceptable(self) -> bool:
        return self.total_errores == 0


class _Acumulador:
    """Junta errores respetando el tope, pero contando todos."""

    def __init__(self) -> None:
        self.errores: list[ErrorEntrada] = []
        self.total = 0

    def anotar(self, archivo: str, campo: str, mensaje: str, fila: int | None = None) -> None:
        self.total += 1
        if len(self.errores) < MAXIMO_ERRORES:
            self.errores.append(ErrorEntrada(archivo=archivo, campo=campo, mensaje=mensaje, fila=fila))


def _leer_fecha(valor: str) -> date | None:
    try:
        return date.fromisoformat(valor.strip())
    except ValueError:
        return None


def _leer_entero(valor: str) -> int | None:
    texto = valor.strip()
    if not texto:
        return None
    # Una hoja de cálculo entrega "12" como "12.0"; sigue siendo entero.
    if texto.endswith(".0"):
        texto = texto[:-2]
    try:
        return int(texto)
    except ValueError:
        return None


def _leer_decimal(valor: str) -> Decimal | None:
    texto = valor.strip()
    if not texto:
        return None
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        return None
    # Decimal acepta "NaN" e "Infinity": no son cantidades y su exponente no es int.
    if not numero.is_finite():
        return None
    return numero


def _validar_productos(
    hoja: Hoja, acumulador: _Acumulador, skus_permitidos: set[str] | None
) -> list[FilaProducto]:
    """Valida la hoja de productos.

    `skus_permitidos` es la lista curada de `lista_productos_precios_limpia.md`
    cuando la carga usa el dataset bakery: el SKU externo es el nombre del
    artículo del CSV, así que un SKU fuera de esa lista nunca aparecerá en las
    ventas y suele ser un nombre mal tecleado.
    """
    filas: list[FilaProducto] = []
    codigos: dict[str, int] = {}
    skus: dict[str, int] = {}
    for numero, valores in hoja.filas:
        codigo = valores["codigo"].strip()
        nombre = valores["nombre"].strip()
        sku = valores["sku_externo"].strip()
        demostrar_texto = valores["demostrar"].strip().lower()

        if not codigo:
            acumulador.anotar(hoja.archivo, "codigo", "El código no puede estar vacío.", numero)
        elif codigo in codigos:
            acumulador.anotar(
                hoja.archivo, "codigo", f"El código {codigo!r} ya aparece en la fila {codigos[codigo]}.", numero
            )
        else:
            codigos[codigo] = numero

        if not nombre:
            acumulador.anotar(hoja.archivo, "nombre", "El nombre no puede estar vacío.", numero)

        if not sku:
            acumulador.anotar(hoja.archivo, "sku_externo", "El SKU externo no puede estar vacío.", numero)
        elif sku in skus:
            acumulador.anotar(
                hoja.archivo, "sku_externo", f"El SKU {sku!r} ya aparece en la fila {skus[sku]}.", numero
            )
        else:
            skus[sku] = numero
            if skus_permitidos is not None and sku not in skus_permitidos:
                acumulador.anotar(
                    hoja.archivo,
                    "sku_externo",
                    f"El SKU {sku!r} no está en la lista curada de productos del dataset.",
                    numero,
                )

        if demostrar_texto not in ("si", "no"):
            acumulador.anotar(
                hoja.archivo, "demostrar", "Debe ser 'si' o 'no'.", numero
            )
            continue

        if codigo and nombre and sku:
            filas.append(
                FilaProducto(codigo=codigo, nombre=nombre, sku_externo=sku, demostrar=demostrar_texto == "si")
            )

    seleccionados = [fila for fila in filas if fila.demostrar]
    if not 3 <= len(seleccionados) <= 5:
        acumulador.anotar(
            hoja.archivo,
            "demostrar",
            f"La demo necesita entre 3 y 5 productos con demostrar='si'; hay {len(seleccionados)}.",
        )
    return filas


def _validar_ingredientes(hoja: Hoja, acumulador: _Acumulador) -> list[FilaIngrediente]:
    filas: list[FilaIngrediente] = []
    codigos: dict[str, int] = {}
    for numero, valores in hoja.filas:
        codigo = valores["codigo"].strip()
        nombre = valores["nombre"].strip()
        unidad = valores["unidad_base"].strip().lower()

        if not codigo:
            acumulador.anotar(hoja.archivo, "codigo", "El código no puede estar vacío.", numero)
        elif codigo in codigos:
            acumulador.anotar(
                hoja.archivo, "codigo", f"El código {codigo!r} ya aparece en la fila {codigos[codigo]}.", numero
            )
        else:
            codigos[codigo] = numero

        if not nombre:
            acumulador.anotar(hoja.archivo, "nombre", "El nombre no puede estar vacío.", numero)

        if unidad not in UNIDADES_BASE:
            acumulador.anotar(
                hoja.archivo,
                "unidad_base",
                f"Unidad no permitida {unidad!r}. Usa una de: {', '.join(UNIDADES_BASE)}.",
                numero,
            )
            continue

        if codigo and nombre:
            filas.append(FilaIngrediente(codigo=codigo, nombre=nombre, unidad_base=unidad))
    return filas


def _validar_recetas(
    hoja: Hoja,
    acumulador: _Acumulador,
    codigos_producto: set[str],
    codigos_ingrediente: set[str],
) -> list[FilaReceta]:
    filas: list[FilaReceta] = []
    vistos: dict[tuple[str, str], int] = {}
    for numero, valores in hoja.filas:
        codigo_producto = valores["codigo_producto"].strip()
        codigo_ingrediente = valores["codigo_ingrediente"].strip()
        cantidad = _leer_decimal(valores["cantidad_por_unidad"])

        if codigo_producto not in codigos_producto:
            acumulador.anotar(
                hoja.archivo,
                "codigo_producto",
                f"No hay producto {codigo_producto!r} en la hoja productos.",
                numero,
            )
        if codigo_ingrediente not in codigos_ingrediente:
            acumulador.anotar(
                hoja.archivo,
                "codigo_ingrediente",
                f"No hay ingrediente {codigo_ingrediente!r} en la hoja ingredientes.",
                numero,
            )

        pareja = (codigo_producto, codigo_ingrediente)
        if pareja in vistos:
            acumulador.anotar(
                hoja.archivo,
                "codigo_ingrediente",
                f"La pareja ya aparece en la fila {vistos[pareja]}; usa una sola línea por ingrediente.",
                numero,
            )
        else:
            vistos[pareja] = numero

        if cantidad is None:
            acumulador.anotar(
                hoja.archivo,
                "cantidad_por_unidad",
                "Cantidad decimal inválida. Usa punto como separador, por ejemplo 0.250.",
                numero,
            )
            continue
        if cantidad <= 0:
            acumulador.anotar(
                hoja.archivo, "cantidad_por_unidad", "La cantidad debe ser mayor que cero.", numero
            )
            continue

        if codigo_producto in codigos_producto and codigo_ingrediente in codigos_ingrediente:
            filas.append(
                FilaReceta(
                    codigo_producto=codigo_producto,
                    codigo_ingrediente=codigo_ingrediente,
                    cantidad_por_unidad=cantidad,
                )
            )
    return filas


def _validar_stock(
    hoja: Hoja,
    acumulador: _Acumulador,
    codigos_producto: set[str],
    codigos_ingrediente: set[str],
) -> tuple[list[FilaStock], set[tuple[str, str]]]:
    """Valida la hoja de stock.

    Devuelve las filas aceptadas y los pares `(tipo, codigo)` que aparecieron en
    la hoja aunque su fila fuera inválida: la cobertura usa el segundo conjunto
    para no reportar «falta la fila» por un fallo que ya se señaló en esa fila.
    """
    filas: list[FilaStock] = []
    declarados: set[tuple[str, str]] = set()
    vistos: dict[tuple[str, str, str], int] = {}
    for numero, valores in hoja.filas:
        tipo = valores["tipo"].strip().lower()
        codigo = valores["codigo"].strip()
        lote = valores["codigo_lote"].strip() or None
        caducidad_texto = valores["fecha_caducidad"].strip()
        limite_texto = valores["fecha_limite_venta"].strip()

        if tipo not in TIPOS_STOCK:
            acumulador.anotar(
                hoja.archivo, "tipo", f"Debe ser 'producto' o 'ingrediente'; llegó {tipo!r}.", numero
            )
            continue

        catalogo = codigos_producto if tipo == "producto" else codigos_ingrediente
        if codigo not in catalogo:
            acumulador.anotar(
                hoja.archivo, "codigo", f"No hay {tipo} {codigo!r} en el catálogo entregado.", numero
            )
        declarados.add((tipo, codigo))

        cantidad = _leer_decimal(valores["cantidad"])
        if cantidad is None:
            acumulador.anotar(hoja.archivo, "cantidad", "Cantidad inválida.", numero)
            continue
        if cantidad < 0:
            acumulador.anotar(hoja.archivo, "cantidad", "La cantidad no puede ser negativa.", numero)
            continue
        if tipo == "producto" and cantidad != cantidad.to_integral_value():
            acumulador.anotar(
                hoja.archivo, "cantidad", "El stock de producto terminado se cuenta en unidades enteras.", numero
            )
            continue
        if tipo == "ingrediente" and -cantidad.as_tuple().exponent > DECIMALES_INGREDIENTE:
            acumulador.anotar(
                hoja.archivo,
                "cantidad",
                f"El ingrediente admite hasta {DECIMALES_INGREDIENTE} decimales en su unidad base.",
                numero,
            )
            continue

        caducidad = _leer_fecha(caducidad_texto) if caducidad_texto else None
        if caducidad_texto and caducidad is None:
            acumulador.anotar(hoja.archivo, "fecha_caducidad", "Usa el formato YYYY-MM-DD.", numero)
            continue

        limite = _leer_fecha(limite_texto) if limite_texto else None
        if limite_texto and limite is None:
            acumulador.anotar(hoja.archivo, "fecha_limite_venta", "Usa el formato YYYY-MM-DD.", numero)
            continue
        if limite is not None and tipo != "producto":
            acumulador.anotar(
                hoja.archivo,
                "fecha_limite_venta",
                "La fecha límite de venta solo aplica a producto terminado.",
                numero,
            )
            continue
        if limite is not None and caducidad is not None and limite > caducidad:
            acumulador.anotar(
                hoja.archivo,
                "fecha_limite_venta",
                "El límite de venta no puede ser posterior a la caducidad.",
                numero,
            )
            continue

        clave = (tipo, codigo, lote or "")
        if clave in vistos:
            acumulador.anotar(
                hoja.archivo,
                "codigo_lote",
                f"El mismo lote de {codigo!r} ya aparece en la fila {vistos[clave]}.",
                numero,
            )
            continue
        vistos[clave] = numero

        if codigo in catalogo:
            filas.append(
                FilaStock(
                    tipo=tipo,
                    codigo=codigo,
                    cantidad=cantidad,
                    codigo_lote=lote,
                    fecha_caducidad=caducidad,
                    fecha_limite_venta=limite,
                )
            )
    return filas, declarados


def _validar_ventas(
    hoja: Hoja, acumulador: _Acumulador, skus_catalogo: set[str]
) -> tuple[list[FilaVenta], tuple[date | None, date | None], int]:
    filas: list[FilaVenta] = []
    vistos: dict[tuple[str, str], int] = {}
    primera: date | None = None
    ultima: date | None = None
    skus_vistos: set[str] = set()

    for numero, valores in hoja.filas:
        fecha_texto = valores["fecha_local"].strip()
        sku = valores["sku_externo"].strip()
        fecha = _leer_fecha(fecha_texto)

        if fecha is None:
            acumulador.anotar(
                hoja.archivo, "fecha_local", f"Fecha inválida {fecha_texto!r}. Usa YYYY-MM-DD.", numero
            )
            continue
        if not sku:
            acumulador.anotar(hoja.archivo, "sku_externo", "El SKU externo no puede estar vacío.", numero)
            continue
        if sku not in skus_catalogo:
            acumulador.anotar(
                hoja.archivo,
                "sku_externo",
                f"El SKU {sku!r} no está en la hoja productos; no se crean productos implícitos.",
                numero,
            )
            continue

        clave = (fecha_texto, sku)
        if clave in vistos:
            acumulador.anotar(
                hoja.archivo,
                "sku_externo",
                f"Ya hay una fila para {sku!r} el {fecha_texto} en la fila {vistos[clave]}; "
                "se espera una fila por fecha y SKU.",
                numero,
            )
            continue
        vistos[clave] = numero

        unidades = _leer_entero(valores["unidades_vendidas"])
        if unidades is None:
            acumulador.anotar(
                hoja.archivo, "unidades_vendidas", "Debe ser un entero; deja la fila fuera si el dato es desconocido.", numero
            )
            continue
        if unidades < 0:
            acumulador.anotar(
                hoja.archivo,
                "unidades_vendidas",
                "No puede ser negativo. Las devoluciones no se netean en esta demo.",
                numero,
            )
            continue

        filas.append(FilaVenta(fecha_local=fecha, sku_externo=sku, unidades_vendidas=unidades))
        skus_vistos.add(sku)
        primera = fecha if primera is None or fecha < primera else primera
        ultima = fecha if ultima is None or fecha > ultima else ultima

    return filas, (primera, ultima), len(skus_vistos)


def _validar_cobertura_stock(
    acumulador: _Acumulador,
    archivo: str,
    productos_demo: list[FilaProducto],
    recetas: list[FilaReceta],
    declarados: set[tuple[str, str]],
) -> None:
    """Exige una fila de stock por cada producto de demo y cada ingrediente suyo.

    La ausencia significa stock desconocido, y un plan no se calcula sobre un
    desconocido. Una fila explícita de `0` sí sirve.
    """
    con_stock = declarados
    codigos_demo = {producto.codigo for producto in productos_demo}

    for producto in productos_demo:
        if ("producto", producto.codigo) not in con_stock:
            acumulador.anotar(
                archivo,
                "codigo",
                f"Falta la fila de stock del producto {producto.codigo!r}. "
                "Si no hay existencias, declara la cantidad 0; la ausencia significa desconocido.",
            )

    ingredientes_demo = {
        receta.codigo_ingrediente for receta in recetas if receta.codigo_producto in codigos_demo
    }
    for codigo in sorted(ingredientes_demo):
        if ("ingrediente", codigo) not in con_stock:
            acumulador.anotar(
                archivo,
                "codigo",
                f"Falta la fila de stock del ingrediente {codigo!r} usado por una receta de demo. "
                "Declara la cantidad 0 si no hay existencias.",
            )


def _validar_recetas_completas(
    acumulador: _Acumulador, archivo: str, productos_demo: list[FilaProducto], recetas: list[FilaReceta]
) -> None:
    con_receta = {receta.codigo_producto for receta in recetas}
    for producto in productos_demo:
        if producto.codigo not in con_receta:
            acumulador.anotar(
                archivo,
                "codigo_producto",
                f"El producto {producto.codigo!r} está marcado para demo pero no tiene receta.",
            )


def validar_entrega(
    hojas: dict[str, Hoja],
    fecha_objetivo_demo: date,
    fecha_referencia_stock: date,
    skus_permitidos: set[str] | None = None,
) -> ResultadoValidacion:
    """Valida el lote completo y devuelve la vista previa.

    No escribe nada. Solo se puede confirmar la carga si `aceptable` es verdadero.
    """
    acumulador = _Acumulador()

    if fecha_referencia_stock >= fecha_objetivo_demo:
        acumulador.anotar(
            "solicitud",
            "fecha_referencia_stock",
            "La referencia de stock debe ser anterior a la fecha objetivo de la demo.",
        )

    productos = _validar_productos(hojas["productos"], acumulador, skus_permitidos)
    ingredientes = _validar_ingredientes(hojas["ingredientes"], acumulador)

    codigos_producto = {producto.codigo for producto in productos}
    codigos_ingrediente = {ingrediente.codigo for ingrediente in ingredientes}
    skus_catalogo = {producto.sku_externo for producto in productos}

    recetas = _validar_recetas(hojas["recetas"], acumulador, codigos_producto, codigos_ingrediente)
    stock, stock_declarado = _validar_stock(
        hojas["stock_inicial"], acumulador, codigos_producto, codigos_ingrediente
    )
    ventas, fechas, skus_en_ventas = _validar_ventas(hojas["ventas"], acumulador, skus_catalogo)

    productos_demo = [producto for producto in productos if producto.demostrar]
    _validar_recetas_completas(acumulador, hojas["recetas"].archivo, productos_demo, recetas)
    _validar_cobertura_stock(
        acumulador, hojas["stock_inicial"].archivo, productos_demo, recetas, stock_declarado
    )

    entrada = EntradaValidada(
        productos=productos,
        ingredientes=ingredientes,
        recetas=recetas,
        stock=stock,
        ventas=ventas,
        fecha_objetivo_demo=fecha_objetivo_demo,
        fecha_referencia_stock=fecha_referencia_stock,
    )
    return ResultadoValidacion(
        entrada=entrada,
        errores=acumulador.errores,
        total_errores=acumulador.total,
        filas_por_hoja={nombre: len(hoja) for nombre, hoja in hojas.items()},
        fechas_ventas=fechas,
        skus_en_ventas=skus_en_ventas,
    )
