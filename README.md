# FoodSave

Prototipo universitario que automatiza la planificación de producción y el abastecimiento de un negocio de alimentos perecibles para prevenir desperdicio (ODS 12). Corre en **una instalación local, para un comercio y una sucursal** ([ADR-005](docs/arquitectura/decisiones/ADR-005-instalacion-local-mvp.md)).

**Fuentes que mandan**, en este orden: [alcance del prototipo](docs/guia-inicio-desarrollo.md) → ADR-005 a ADR-008 → [contratos](docs/api/contratos.md) y [esquema](docs/base_de_datos/esquema-objetivo-mvp.md) → [responsabilidades](docs/equipo/responsabilidades.md). Lo que queda fuera de la demo está en [visión futura](docs/vision-futura.md).

## Arranque local de desarrollo

1. Instala Docker con Compose y copia `.env.example` a `.env`. Cambia `POSTGRES_PASSWORD` por una clave alfanumérica larga y `JWT_SECRET` por una cadena aleatoria larga; no subas `.env` a Git. `TELEGRAM_BOT_TOKEN` queda vacío hasta configurar y autorizar el canal con un chat propio de pruebas.
Si vienes del corte local con revisión 0008_e03_modelo o 0009_m02_planes, sigue primero el [puente de conciliación](backend/migrations/GUIA_DESARROLLO.md); no reemplaces la revisión sin migrar ni borres volúmenes.

2. Ejecuta `docker compose up --build -d` desde la raíz del repositorio.
3. Comprueba `docker compose exec -T api alembic current --check-heads`. El servicio `migraciones` aplica las revisiones antes de iniciar API, worker y Beat; si falla, corrige el error antes de continuar.
4. Ejecuta `docker compose exec -it api python -m app.core.crear_admin` y escribe el correo y contraseña del administrador.
5. Abre `http://localhost:3000` para iniciar sesión. La API responde en `http://localhost:8000/salud` y su documentación en `http://localhost:8000/docs`.

Para los siguientes arranques en Windows, abre `iniciar-foodsave.cmd` con doble clic: su auxiliar `iniciar-foodsave.ps1` evita arranques simultáneos del lanzador y espera a la API y a la web antes de abrir la pantalla de carga. Si falla, muestra el error real; no borra volúmenes ni contenedores. Tras cambios de código, ejecuta `iniciar-foodsave.cmd -Build` una vez para actualizar las imágenes; los siguientes clics reutilizan esas imágenes. `-NoBrowser` comprueba el arranque sin abrir el navegador. Evita ejecutar otro `docker compose up` al mismo tiempo. El primer build y la creación del administrador siguen siendo tareas de configuración únicas. Desde la pantalla **Cargar CSV**, selecciona `foodsave-ml/bakery_sales_limpio_final.csv`; el catálogo curado se carga automáticamente y el worker prepara el modelo. La pantalla muestra la ejecución y permite reintentar el entrenamiento si falla, sin subir otra vez el archivo.

Cada PC tiene su propio volumen de PostgreSQL y `model_artifacts` compartido: el worker puede guardar el futuro CBM y sus metadatos, y la API lo monta en solo lectura mediante `MODEL_ARTIFACT_DIR=/code/model_artifacts`. El volumen vacío no representa un modelo disponible. `docker compose down` detiene los servicios y conserva los datos; evita `down -v` salvo que quieras borrar intencionalmente ambos volúmenes. Para probar el trabajador: `docker compose exec api python -c "from app.workers.celery_app import tarea_prueba; print(tarea_prueba.delay('ok').get(timeout=15))"`.

## Guía rápida

- [Guías por carpeta y responsable](docs/equipo/mapa-carpetas.md).
- [Dependencias y entregas entre integrantes](docs/equipo/dependencias.md).
- [Registro obligatorio de avances](docs/equipo/avances/README.md).
- [Instrucciones para IA](AGENTS.md).

- [Alcance y criterio de demo del prototipo universitario](docs/guia-inicio-desarrollo.md).
- [Estado real de la base y puertas para desarrollar](docs/base-para-desarrollo.md): decisiones cerradas, brechas y orden de integración.
- [Especificación integral de diseño](docs/diseno/especificacion-visual.md): reglas visuales, pantallas, componentes, estados y accesibilidad.
- [Especificación funcional de módulos](docs/funcionalidades/especificacion-modulos.md): qué muestra y permite hacer cada sección.
- [Cronograma semanal](docs/equipo/cronograma.md): hitos de las semanas 1 a 16 y estado de cada entrega.
- [Responsabilidades del equipo](docs/equipo/responsabilidades.md): cada persona desarrolla interfaz, servidor y API de los módulos asignados.
- [Arquitectura y diagramas](docs/arquitectura/diagramas/README.md), incluido el [diagrama entidad-relación](docs/base_de_datos/diagrama-entidad-relacion.md).
- [Contratos de API](docs/api/contratos.md) y [rutas propuestas](docs/api/rutas-api.md).
- [Índice de documentación](docs/README.md) y [referencias visuales conservadas](docs/diseno/mockups/README.md).

## Organización del repositorio

| Carpeta | Propósito |
|---|---|
| [`docs/`](docs/README.md) | Arquitectura, diseño, funcionalidades, API, datos, automatización y equipo |
| [`frontend/`](frontend/README.md) | Interfaz Next.js y funciones por dominio |
| [`backend/`](backend/README.md) | API FastAPI, módulos, trabajos asíncronos y pruebas |
| [`scripts/`](scripts/README.md) | Herramientas de apoyo del equipo |
| [`.github/workflows/`](.github/workflows/README.md) | Flujos de integración continua |

La distribución del trabajo es por **módulo completo**: su responsable implementa interfaz, servidor, rutas de API, pruebas e integración de cada módulo asignado. Todos los módulos tienen un responsable asignado; la sección 16 detalla la propiedad de cada uno.

## Estado del proyecto

El núcleo de desarrollo tiene manifiestos, contenedores, migración inicial y acceso básico. El resto de módulos y la integración del modelo aún están pendientes. El cronograma histórico separa hitos comunicados por el equipo de objetivos propuestos; no representa por sí solo el estado actual del código.

`README.md`, `src/app`, `public` y `.github/workflows` conservan sus nombres porque las herramientas los requieren. Los nombres propios de tecnologías y la sintaxis de formatos técnicos también se mantienen.

---

# FoodSave — Documento Técnico Maestro

## 1. Propósito

Este documento define la estructura técnica, funcional y organizacional de **FoodSave**. Debe servir como referencia para arquitectura, desarrollo, integración, documentación, pruebas y división del trabajo.

Equipo:
- Axel Cueva
- Edu Sanchez
- Kevin Bohorquez
- Leonardo Vera
- Leonardo Aguirre
- Max Rojas

## 2. Definición del proyecto

**FoodSave es una plataforma de automatización preventiva para negocios que producen y comercializan alimentos perecibles.** En el MVP, cada comercio usa una instalación local independiente.

Analiza ventas, producción, inventario, recetas, insumos, proveedores, excedentes y desperdicio para:
- predecir demanda;
- generar planes de producción;
- calcular necesidades de insumos;
- detectar faltantes;
- generar y enviar pedidos;
- seleccionar proveedores;
- detectar excedentes;
- activar promociones;
- verificar resultados;
- reintentar ante fallos;
- notificar incidencias;
- registrar resultados;
- alimentar reportes y métricas.

Ciclo principal:

```text
Primera carga (ventas + catálogo + stock) → entrenamiento CatBoost → Beat dispara la propuesta
→ pronóstico → plan de producción → necesidades y faltantes → pedidos por proveedor
→ aprobación configurable → mensaje real por Telegram a un chat de pruebas
→ evaluación pronóstico vs. venta real → ajuste de stock → sugerencia de promoción
```

Cada paso automático queda como ejecución durable con intentos, estado y error. Fórmulas, estados y criterio de demo completa: [guía de alcance](docs/guia-inicio-desarrollo.md).

## Arranque local

1. Instala Docker con Compose y copia `.env.example` a `.env`. Define `POSTGRES_PASSWORD` (alfanumérica larga) y `JWT_SECRET` (aleatoria larga). `TELEGRAM_BOT_TOKEN` queda vacío hasta que exista el canal (L03).
2. `docker compose up --build -d`. El servicio `migraciones` aplica Alembic antes de iniciar `api`, `worker` y `beat`.
3. Verifica: `docker compose exec -T api alembic current --check-heads`.
4. Crea el administrador: `docker compose exec -it api python -m app.core.crear_admin`.
5. Web en `http://localhost:3000`; API en `http://localhost:8000/salud` y `/docs`.

En Windows, los arranques siguientes se hacen con `iniciar-foodsave.cmd`. Para cargar datos rápido, abre **CSV piloto** (`/inicializacion/piloto`) y sube `foodsave-ml/bakery_sales_limpio_final.csv`; el worker prepara el modelo. Para comprobar el worker: `docker compose exec api python -c "from app.workers.celery_app import tarea_prueba; print(tarea_prueba.delay('ok').get(timeout=15))"`. `docker compose down` conserva los datos; `down -v` borra los volúmenes `postgres_data` y `model_artifacts`.

### Pruebas

```bash
pip install -e './backend[test,ml]'
pytest backend/tests foodsave-ml/tests -q        # sin ml, falla test_pronosticos_k02_k03
cd frontend && npm ci && npm run typecheck
```

Las pruebas de concurrencia requieren PostgreSQL/Redis y se activan con `A03_POSTGRES_TEST=1` y `V02_POSTGRES_TEST=1` (así las corre el CI).

## Tecnologías

| Capa | Uso real |
|---|---|
| Interfaz | Next.js 15, React 19, TypeScript, CSS propio (`src/app/styles.css`), gráficos SVG propios |
| Servidor | Python 3.12, FastAPI, Pydantic, SQLAlchemy 2, Alembic, PyJWT, pwdlib (Argon2) |
| Datos | PostgreSQL 16 |
| Automatización | Celery + Redis 7 + Celery Beat |
| Modelo | pandas, NumPy, CatBoost (scikit-learn como apoyo) |
| Infraestructura | Docker Compose: `postgres`, `redis`, `migraciones`, `api`, `worker`, `beat`, `frontend` |
| CI | GitHub Actions ([base-ci.yml](.github/workflows/base-ci.yml)) |

Arquitectura: **monolito modular** con trabajadores asíncronos ([ADR-001](docs/arquitectura/decisiones/ADR-001-monolito-modular.md), [visión general](docs/arquitectura/vision_general.md)).

## Variables de entorno

| Variable | Uso |
|---|---|
| `POSTGRES_PASSWORD` | Clave de PostgreSQL; Compose arma `DATABASE_URL` |
| `JWT_SECRET` | Firma de tokens (expiran a los 30 min; no hay renovación) |
| `TELEGRAM_BOT_TOKEN` | Opcional hasta L03 |
| `ML_COMERCIO_ID`, `ML_SUCURSAL_ID` | Identidad externa del dataset (`piloto` / `principal`) |

Compose fija además `REDIS_URL`, `FRONTEND_ORIGIN` y `MODEL_ARTIFACT_DIR`. Nunca subir `.env`.

## Equipo y estado

| Responsable | Bloque | Estado (06-10-2026) |
|---|---|---|
| Axel Cueva | Acceso, configuración, motor de automatizaciones, infraestructura | A01–A04 listos para integrar |
| Edu Sanchez | Primera carga, productos, ventas, estructura visual común | E01–E04 listos para integrar |
| Kevin Bohorquez | Entrenamiento, inferencia, evaluación histórica, panel histórico | K01–K04 listos para integrar |
| Leonardo Vera | Inventario por lotes, promociones sugeridas | V01–V02 listos (hechos por Max); V03 pendiente; V04 parcial |
| Leonardo Aguirre | Proveedores, pedidos, Telegram | L01 parcial (API sin UI); L02–L04 pendientes |
| Max Rojas | Ingredientes, recetas, planificación | M01 listo para integrar; M02–M04 pendientes |

Detalle y evidencia en [avances](docs/equipo/avances/README.md). Migraciones aplicadas: `0001_nucleo` → `0001a` → `0001b` → `0001c` → `0002_e01_ventas` → `0003_pronosticos` → `0004_e03_inicializacion` → `0005_m01_ingredientes_recetas` → `0006_v01_inventario` → `0007_l01_proveedores`.

## Organización

| Carpeta | Contenido |
|---|---|
| [`docs/`](docs/README.md) | Alcance, arquitectura, diseño, funcionalidades, API, datos, automatización, equipo |
| [`frontend/`](frontend/README.md) | Next.js; `src/app` (pantallas), `components`, `services`, `types` |
| [`backend/`](backend/README.md) | FastAPI; `app/modules/<dominio>`, `app/workers`, `migrations`, `tests` |
| [`foodsave-ml/`](foodsave-ml/README.md) | Entrenamiento, evaluación y contratos del modelo |
| [`.github/workflows/`](.github/workflows/README.md) | CI |

Cada carpeta tiene `GUIA_DESARROLLO.md` (responsable, alcance, tareas). Índice: [mapa de carpetas](docs/equipo/mapa-carpetas.md). Instrucciones para IA: [AGENTS.md](AGENTS.md).

## Reglas de trabajo

- Módulo por responsable: interfaz, API, datos y pruebas de su bloque. Un módulo usa los servicios públicos de otro, nunca sus modelos o repositorio.
- Los servicios hacen `flush` y no `commit`; confirma la ruta o el orquestador.
- API en `/api/v1`. Éxito: `{"datos": …, "metadatos": …}`. Error: `{"error": {"codigo", "mensaje", "detalles?"}}`. Códigos en el [catálogo de errores](docs/api/errores.md).
- Nombres: Python `snake_case`, clases y componentes `PascalCase`, TypeScript `camelCase`, rutas `kebab-case`.
- Git: rama permanente por apellido (`cueva`, `sanchez`, `bohorquez`, `vera`, `aguirre`, `rojas`); `main` estable; integración por PR con pruebas verdes. Mensajes `funcion(modulo): …`, `correccion(modulo): …`, `prueba(modulo): …`. Ver [flujo Git](docs/equipo/flujo-git.md).
- Al cerrar un avance, actualizar el registro propio en [avances](docs/equipo/avances/README.md) y el contrato si cambió.
