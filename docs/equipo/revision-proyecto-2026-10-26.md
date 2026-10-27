# Revisión del proyecto · 26-10-2026

Codex por solicitud del usuario: fetch, pull y revisión de pendientes. Rama `bohorquez`, HEAD `39723b4`. Coordinación transversal A04 (Cueva); seguimiento de la sesión en Bohorquez, sin atribuir implementación a los integrantes.

## Sincronización

- `git fetch origin` correcto; `git pull --ff-only origin bohorquez`: Already up to date.
- `HEAD`, `origin/bohorquez` y `origin/main` coinciden; comparación con main: 0/0 commits. Incluye PR #16 y #17. No requiere merge adicional.
- Se conserva `docs/automatizacion/bpmn/`, carpeta local sin seguimiento. No se cambia de rama, publica ni modifica código de negocio.

## Pendientes actuales, en orden recomendado

| Prioridad | Responsable | Pendiente y evidencia |
|---|---|---|
| 1 | Rojas, revisión de Edu/Vera/Axel | Completar tienda T01/T03/T04/T05: precios/configuración, catálogo/cotización reales, pedidos persistentes, retiro FEFO transaccional y promociones aprobadas. `backend/app/modules/tienda/rutas.py` solo expone sesión Google y sesión actual; `modelos.py` solo define cliente. `frontend/src/tienda/servicios.ts` usa modo ejemplo por defecto y guarda stock/pedidos en localStorage. La interfaz no acredita integración con inventario ni PostgreSQL. |
| 2 | Rojas/Axel | Verificar Google con cuenta real y configuración OAuth, sin presumir el estado de secretos locales. T02 tiene implementación y pruebas aisladas. Para la futura tienda real, propagar `NEXT_PUBLIC_TIENDA_MODO=api` al build: actualmente Compose/Dockerfile solo cablean API URL y Google client ID. Configurar Google por sí solo no cambia el catálogo de ejemplo. |
| 3 | Rojas/Axel | Retirar del índice, en una corrección posterior, `backend/.local/`: hay 557 archivos versionados, 553 bajo site-packages. `.gitignore` cubre `.venv*`, pero no esa ruta. No se borran archivos durante esta revisión. |
| 4 | Todos, coordinación Cueva | Cierre del corte actual desde base aislada con PostgreSQL/Redis: migraciones → carga → modelo → Beat → plan → necesidades → compras → métricas/promociones. Docker no responde en esta máquina. Comprobar CI remoto y reproducción por otro integrante, respaldo/restauración de base, artefactos y secretos. `scripts/` solo contiene documentación. |
| 5 | Aguirre/Cueva | Demo automática Telegram a chat propio con autorización expresa y evidencia persistida; revisar ofertas/destino reales de la instalación. Esta tarea no autoriza mensajes y no se enviaron. WhatsApp sigue sin adaptador acreditado por esta revisión. |
| 6 | Edu/Rojas/Aguirre | Paginación remota pendiente: productos limita a 500 filas; planes y propuestas a 50. Pronósticos ya pagina modelos/corridas: no volver a incluirlo como defecto pendiente del corte del 20-10. |
| 7 | Edu y cada dueño de pantalla | Añadir pruebas repetibles de navegador para los recorridos críticos. `frontend/package.json` tiene dev/build/start/typecheck, sin runner de comportamiento. La compilación no sustituye la prueba de compra real o recuperación. |
| 8 | Dueños documentales | Conciliar resúmenes y contratos con main. `contrato-tienda.md` comienza con «ninguna existe todavía» aunque su sección T02 documenta las dos rutas implementadas. Responsabilidades aún rotula toda la tienda como diseño. El informe del 20-10 contiene pendientes históricos ya corregidos y exclusiones posteriormente ampliadas (recepción/tienda); leer las ampliaciones y registros recientes. |

K01–K04 y M01–M04 ya tienen código y consumidores; no corresponde reconstruirlos. R01–R03 del informe anterior tienen correcciones existentes. Operación con ventas actuales, validación comercial del modelo y WhatsApp son ampliaciones distintas del cierre del prototipo histórico. Los pagos de tienda permanecen simulados conforme ADR-009.

## Verificaciones ejecutadas

- `npm run typecheck` desde frontend: salida 0.
- `python -m pytest backend/tests/integration/test_tienda_sesion.py backend/tests/integration/test_evaluacion_revisiones.py backend/tests/integration/test_migraciones_entregas.py -q --tb=short`: **19 passed, 19 warnings, 11,36 s**. SQLite temporal; no Google externo, mensajes ni datos habituales. Advertencias de Starlette/httpx y reflexión SQLite de índices por expresión.
- Entorno Python 3.13 con PYTHONPATH a backend, `.tmp/revision-deps`, pruebas de integración y foodsave-ml; TEMP/TMP en `.tmp/revision-runtime` y autodescubrimiento de plugins pytest desactivado. El primer intento en sandbox no devolvió resultado; la ejecución fuera del sandbox sí completó. No se cuenta el intento sin resultado como prueba aprobada.
- `docker info --format '{{.ServerVersion}}'`: falla por ausencia del pipe dockerDesktopLinuxEngine. No se arrancan servicios habituales ni se aplican migraciones a su base.
- No se ejecutan build, suite completa, QA visual, CI remoto, validación Google real ni reproducción en otra PC en esta revisión.

Entrega documental local, sin commit/PR. Siguiente paso: completar la frontera real de tienda por T01/T03 antes de conectar el checkout con inventario; en paralelo, verificar infraestructura y corregir el versionado de dependencias con sus responsables.
