# Puerta de arranque de los módulos del prototipo

Esta guía aplica al [alcance universitario congelado](../guia-inicio-desarrollo.md) y a las [puertas de integración](../base-para-desarrollo.md). El código actual incluye acceso, configuración y motor A03; los manejadores de dominio siguen pendientes. Aprobar esta puerta no significa que la demo completa ya funcione.

## Comprobación en cada computadora

1. Clonar el repositorio, copiar `.env.example` a `.env` y elegir claves locales propias.
2. Levantar los servicios con `docker compose up --build -d`.
3. Confirmar que `docker compose exec -T api alembic current --check-heads` termina correctamente; Compose ya aplicó las migraciones. Crear el administrador con `docker compose exec -it api python -m app.core.crear_admin`.
4. Comprobar `GET http://localhost:8000/salud`, iniciar sesión en `http://localhost:3000` y abrir la configuración del comercio local.
5. Ejecutar la tarea de prueba de Celery descrita en el README principal. `docker compose ps` debe mostrar PostgreSQL y Redis saludables, API, worker, Beat y frontend activos. El servicio `migraciones` termina con código cero.

En Windows, después de configurar `.env` y construir imágenes una vez, `iniciar-foodsave.cmd` ejecuta `docker compose up -d` y abre `/inicializacion/piloto` cuando la web responde. La carga web del CSV bakery permite probar E01→K01/K03 sin copiar el archivo al contenedor. El asistente completo está en `/inicializacion`; hasta conectar Max y Vera no cierra recetas ni stock.

Una segunda persona debe completar esos pasos en su computadora antes de declarar reproducible el núcleo. Registrar sistema operativo, versión de Docker, salida de migración, prueba de worker y fallos encontrados en la solicitud de incorporación. El volumen `model_artifacts` comienza vacío y es compartido entre worker (escritura) y API (solo lectura); la carga web piloto puede generar CBM y `metadata.json` reales mediante el código de Kevin. `TELEGRAM_BOT_TOKEN` puede quedar vacío hasta que Aguirre entregue la integración de un chat propio; no se envía ningún mensaje durante esta comprobación.

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
