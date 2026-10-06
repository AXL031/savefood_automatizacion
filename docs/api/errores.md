# Catálogo de códigos de error

Generado desde `backend/app` el 06-10-2026. Sobre de error y significado de cada HTTP: [convenciones](contratos.md#convenciones-http). Un código nuevo se agrega aquí en el mismo cambio que lo introduce.

## Genéricos (`core/errores.py`)

| HTTP | Código |
|---|---|
| 400 | `SOLICITUD_INVALIDA` |
| 401 | `AUTENTICACION_REQUERIDA` |
| 403 | `PERMISO_DENEGADO` |
| 404 | `NO_ENCONTRADO` |
| 405 | `METODO_NO_PERMITIDO` |
| 409 | `CONFLICTO` |
| 422 | `DATOS_INVALIDOS` (incluye `detalles`) |
| 500 | `ERROR_INTERNO` |
| 503 | `SERVICIO_NO_DISPONIBLE` |

## Usados por varios módulos

| HTTP | Código | Módulos |
|---|---|---|
| 409 | `CLAVE_REUTILIZADA` | automatizaciones, inventario, pronosticos, ventas |
| 409 | `MAPEO_AMBIGUO` | productos, ventas |
| 409/422 | `CODIGO_DUPLICADO` | ingredientes, productos |
| 422 | `CANTIDAD_INVALIDA` | inventario, recetas |
| 422 | `CATALOGO_FALTANTE` | pronosticos, ventas |
| 422 | `CLAVE_INVALIDA` | inventario, pronosticos, ventas |
| 422 | `MOTIVO_OBLIGATORIO` | inventario, recetas |
| 422 | `REFERENCIA_ROTA` | inventario, recetas |
| 422 | `SKU_DESCONOCIDO` | inicializacion, productos, ventas |

## Negocios

| HTTP | Código |
|---|---|
| 503 | `NEGOCIO_NO_CONFIGURADO` |

## Automatizaciones

| HTTP | Código |
|---|---|
| 400 | `HORA_NO_FUTURA` |
| 404 | `EJECUCION_NO_ENCONTRADA` |
| 404 | `INTENTO_NO_ENCONTRADO` |
| 404 | `PROGRAMACION_NO_ENCONTRADA` |
| 409 | `EJECUCION_NO_INICIABLE` |
| 409 | `INTENTOS_AGOTADOS` |
| 409 | `INTENTO_NO_ACTIVO` |

## Inicializacion

| HTTP | Código |
|---|---|
| 409 | `TRANSICION_INVALIDA` |
| 409 | `YA_INICIALIZADA` |
| 413 | `ARCHIVO_DEMASIADO_GRANDE` |
| 422 | `ARCHIVO_ILEGIBLE` |
| 422 | `ARCHIVO_INVALIDO` |
| 422 | `ARCHIVO_REPETIDO` |
| 422 | `ARCHIVO_SIN_NOMBRE` |
| 422 | `ARCHIVO_VACIO` |
| 422 | `CARGA_INVALIDA` |
| 422 | `ENCABEZADO_INVALIDO` |
| 422 | `ENTREGA_INCOMPLETA` |
| 422 | `ENTREGA_VACIA` |
| 422 | `HOJA_AUSENTE` |
| 503 | `CATALOGO_PILOTO_NO_DISPONIBLE` |
| 503 | `LECTOR_NO_DISPONIBLE` |

## Productos

| HTTP | Código |
|---|---|
| 409 | `CATALOGO_DIFERENTE` |
| 409 | `SKU_INACTIVO` |
| 422 | `CATALOGO_INVALIDO` |

## Ventas

| HTTP | Código |
|---|---|
| 404 | `VENTA_NO_ENCONTRADA` |
| 409 | `VENTA_DUPLICADA` |
| 422 | `CORRECCION_INVALIDA` |
| 422 | `IDENTIDAD_NO_CONFIGURADA` |
| 422 | `RANGO_INVALIDO` |
| 422 | `VENTAS_INVALIDAS` |
| 422 | `VENTAS_VACIAS` |
| 422 | `VENTA_INVALIDA` |

## Pronosticos

| HTTP | Código |
|---|---|
| 404 | `CORRIDA_NO_ENCONTRADA` |
| 404 | `MODELO_NO_ENCONTRADO` |
| 422 | `CORRIDA_INVALIDA` |
| 422 | `FECHA_FUERA_DE_PRUEBA` |
| 422 | `SKU_NO_RESUELTO` |
| 503 | `MODELO_NO_LISTO` |

## Ingredientes

| HTTP | Código |
|---|---|
| 404 | `INGREDIENTE_NO_ENCONTRADO` |
| 409 | `INGREDIENTE_DIFERENTE` |
| 409 | `INGREDIENTE_EN_RECETA_ACTIVA` |
| 409 | `UNIDAD_EN_USO` |
| 422 | `DATO_DEMASIADO_LARGO` |
| 422 | `DATO_OBLIGATORIO` |
| 422 | `UNIDAD_NO_PERMITIDA` |

## Recetas

| HTTP | Código |
|---|---|
| 404 | `PRODUCTO_NO_ENCONTRADO` |
| 404 | `RECETA_NO_ENCONTRADA` |
| 409 | `RECETA_DIFERENTE` |
| 422 | `INGREDIENTE_INACTIVO` |
| 422 | `INGREDIENTE_REPETIDO` |
| 422 | `PAREJA_DUPLICADA` |
| 422 | `PRODUCTO_INACTIVO` |
| 422 | `RECETA_VACIA` |

## Inventario

| HTTP | Código |
|---|---|
| 404 | `LOTE_NO_ENCONTRADO` |
| 409 | `LOTE_EXISTENTE` |
| 409 | `SALDO_INSUFICIENTE` |
| 422 | `CLAVE_OBLIGATORIA` |
| 422 | `FECHA_INVALIDA` |
| 422 | `HORA_INVALIDA` |
| 422 | `LOTE_INVALIDO` |
| 422 | `TIPO_INVALIDO` |
| 422 | `TIPO_OBLIGATORIO` |
| 422 | `VIDA_UTIL_EXCEDIDA` |

## Proveedores

| HTTP | Código |
|---|---|
| 404 | `OFERTA_NO_ENCONTRADA` |
| 404 | `PROVEEDOR_NO_ENCONTRADO` |
| 404 | `REFERENCIA_NO_ENCONTRADA` |
| 409 | `CONFLICTO_PROVEEDORES` |
| 422 | `CHAT_INVALIDO` |

`CODIGO_DUPLICADO` es 409 cuando el código ya existe en la base y 422 cuando se repite dentro del mismo archivo de carga.
