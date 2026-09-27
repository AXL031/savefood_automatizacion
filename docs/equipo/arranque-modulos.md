# Puerta de arranque de los módulos del prototipo

Esta guía aplica al [alcance universitario congelado](../guia-inicio-desarrollo.md) y a las [puertas de integración](../base-para-desarrollo.md). El código actual solo contiene el núcleo de acceso y una tarea de prueba: aprobar esta puerta no significa que la demo ya funcione.

## Comprobación en cada computadora

1. Clonar el repositorio, copiar `.env.example` a `.env` y elegir claves locales propias.
2. Levantar los servicios con `docker compose up --build -d`.
3. Aplicar `docker compose exec api alembic upgrade head` y crear el administrador con `docker compose exec -it api python -m app.core.crear_admin`.
4. Comprobar `GET http://localhost:8000/salud`, iniciar sesión en `http://localhost:3000` y abrir la configuración del comercio local.
5. Ejecutar la tarea de prueba de Celery descrita en el README principal.

Una segunda persona debe completar esos pasos en su computadora antes de declarar reproducible el núcleo. Registrar sistema operativo, versión de Docker, salida de migración, prueba de worker y fallos encontrados en la solicitud de incorporación.

## Primer corte por responsable

Consultar el [reparto detallado](responsabilidades.md), las [dependencias](dependencias.md) y el [registro obligatorio de avances](avances/README.md).

| Responsable | Entrega del prototipo |
|---|---|
| Axel Cueva | Acceso, configuración y motor de automatizaciones. Tareas A01–A04 del reparto vigente. |
| Edu Sanchez | Inicialización, productos, ventas y estructura visual compartida. Tareas E01–E04 del reparto vigente. |
| Kevin Bohorquez | Modelo predictivo, evaluación histórica y dashboard. Tareas K01–K04 del reparto vigente. |
| Leonardo Vera | Inventario por lotes y promociones sugeridas. Tareas V01–V04 del reparto vigente. |
| Leonardo Aguirre | Proveedores, pedidos y Telegram. Tareas L01–L04 del reparto vigente. |
| Max Rojas | Ingredientes, recetas y planificación. Tareas M01–M04 del reparto vigente. |

Cada cambio de dominio incluye modelo, migración, API, interfaz necesaria y prueba de la frontera que modifica. El [esquema `0002`](../base_de_datos/esquema-objetivo-mvp.md) tiene claves cruzadas: acordar primero nombres y restricciones en una revisión conjunta. No reescribir una migración que otro integrante ya haya aplicado.

## Recorrido mínimo integrado

Primera carga de ventas y catálogo → preparación automática de CatBoost → backtest histórico → propuesta programada por Beat → pronóstico, plan, faltantes y pedidos por proveedor → aprobación opcional y envío real a chat de pruebas por Telegram → evaluación posterior frente a la venta conocida → panel con cobertura → ajuste de stock → evaluación programada de promoción sugerida. La misma carga, programación o tarea entregada dos veces conserva un solo efecto local por clave y entrada. El plan, el pedido y la promoción no ejecutan producción física, recepción ni cambios de precio.

La entrega se acepta con el [criterio de demo completa](../guia-inicio-desarrollo.md), no con una pantalla aislada o un servicio que solo funcione manualmente.
