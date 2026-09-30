# Guía de desarrollo — Catálogo de productos y SKU

**Carpeta:** `backend/app/modules/productos`.

**Responsable:** Edu Sanchez. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida. **Tareas:** E01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-importaciones.md](../../../../docs/api/contrato-importaciones.md).
- [docs/arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md](../../../../docs/arquitectura/decisiones/ADR-006-identidades-lotes-pronosticos.md).

## Punto de partida

E01 parcial implementa `producto` y `sku_producto` en `0002_e01_ventas`. `cargar_catalogo_bakery(sesion, lista)` lee la lista curada de nombres y crea mapeos explícitos; `resolver_sku(sesion, origen, sku_externo)` devuelve el ID local o falla con `SKU_DESCONOCIDO`. `listar_skus_bakery(sesion)` y `nombres_productos(sesion, ids)` son lecturas públicas para Kevin y otros consumidores. Ninguna función confirma la transacción. Los precios de la lista son referencia del dataset y no forman parte del catálogo operativo de la demo. API y pantalla de productos siguen pendientes. Consultar el resumen vigente de [Edu Sanchez](../../../../docs/equipo/avances/sanchez.md).

## Trabajo en esta carpeta

1. Validar códigos internos y SKU externos; resolver origen/SKU a producto interno.
2. Crear lecturas y servicios de carga; desactivar catálogo usado sin borrarlo en cascada.
3. Exponer identidad estable a Ventas, Recetas, Inventario y Pronósticos.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `producto`, `sku_producto`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Catálogo de la primera carga y consultas de productos.
- **Entrega:** Producto interno y mapeo activo para consumidores.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- SKU desconocido se rechaza, no crea producto implícito.
- Código/SKU duplicado se informa antes de persistir.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
