# Puerta de arranque de los módulos

Esta guía aplica al MVP local de [ADR-005](../arquitectura/decisiones/ADR-005-instalacion-local-mvp.md). El núcleo ejecutable se entrega antes de que cada responsable incorpore su primera migración de dominio.

## Comprobación en cada computadora

1. Clonar el repositorio, crear `.env` a partir de `.env.example` y elegir claves locales propias.
2. Levantar los servicios con `docker compose up --build -d`.
3. Aplicar `docker compose exec api alembic upgrade head` y crear el administrador con `docker compose exec -it api python -m app.core.crear_admin`.
4. Comprobar `GET http://localhost:8000/salud`, iniciar sesión en `http://localhost:3000` y comprobar que aparece el comercio local.
5. Ejecutar la tarea de prueba de Celery descrita en el README principal.

Una persona distinta a quien preparó la base debe completar estos pasos antes de declarar reproducible el entorno. El resultado se registra en una solicitud de incorporación.

## Entrega de cada responsable

| Responsable | Primer contrato a cerrar | Primer corte implementable |
|---|---|---|
| Axel | Identidad local, estados de ejecución, clave de idempotencia y aviso | Configuración del negocio, permisos y registro de una ejecución de prueba. |
| Edu | Indicadores y componentes visuales compartidos | Navegación y panel que muestre datos reales de los módulos disponibles. |
| Kevin | Unidad de ingrediente, receta, entrada del pronóstico y salida del plan | Ingredientes/recetas y servicio de pronóstico local con versión de modelo. |
| Leonardo Vera | Identidad estable del producto, importación de ventas y saldos | Productos, ventas e inventario con API y persistencia. |
| Leonardo Aguirre | Faltantes, estados de pedido y confirmación | Proveedor, pedido y adaptador de Telegram de prueba. |
| Max | Riesgo, descuento y medición de desperdicio | Detección, promoción y registro de resultado. |

Cada dueño completa los campos y restricciones de sus tablas en el [diccionario](../base_de_datos/diccionario-de-datos.md), acuerda sus contratos de entrada y salida con quienes los consumen, incorpora su migración y verifica su ruta con una prueba significativa. Si dos ramas agregan migraciones en paralelo, se crea una revisión de unión de Alembic o se reordena la segunda migración antes de integrar; nunca se reescribe una migración ya aplicada por el equipo.

## Integración mínima esperada

La primera demostración conectada sigue esta ruta: venta registrada → pronóstico → plan → faltantes → pedido → intento de envío a Telegram → estado del pedido → panel. El estado `ENVIADO` exige respuesta satisfactoria de Telegram; `CONFIRMADO` exige acción explícita del proveedor. Si se corta internet, el pedido permanece pendiente y el reintento queda registrado.
