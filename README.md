# FoodSave

FoodSave permite planificar producción y abastecimiento y prevenir desperdicio de alimentos perecibles. **El MVP acordado es una instalación local por comercio y una sucursal por instalación.** La [decisión de arquitectura del MVP](docs/arquitectura/decisiones/ADR-005-instalacion-local-mvp.md) prevalece sobre las referencias anteriores a SaaS, varias sucursales o filtrado por `negocio_id` en este documento. La comercialización mediante suscripción es una etapa futura.

El núcleo inicial ya incluye una interfaz mínima, API, PostgreSQL, Redis, trabajador y migración de negocio y usuario. Los demás módulos siguen en desarrollo; el [diccionario de datos](docs/base_de_datos/diccionario-de-datos.md) es la propuesta a revisar con sus responsables antes de crear sus tablas.

## Arranque local de desarrollo

1. Instala Docker con Compose y copia `.env.example` a `.env`. Cambia `POSTGRES_PASSWORD` por una clave alfanumérica larga y `JWT_SECRET` por una cadena aleatoria larga; no subas `.env` a Git.
2. Ejecuta `docker compose up --build -d` desde la raíz del repositorio.
3. Ejecuta `docker compose exec api alembic upgrade head` para crear el núcleo de datos.
4. Ejecuta `docker compose exec -it api python -m app.core.crear_admin` y escribe el correo y contraseña del administrador.
5. Abre `http://localhost:3000` para iniciar sesión. La API responde en `http://localhost:8000/salud` y su documentación en `http://localhost:8000/docs`.

Cada PC tiene su propio volumen de PostgreSQL. `docker compose down` detiene los servicios y conserva los datos; evita `down -v` salvo que quieras borrar intencionalmente la base de desarrollo. Para probar el trabajador: `docker compose exec api python -c "from app.workers.celery_app import tarea_prueba; print(tarea_prueba.delay('ok').get(timeout=15))"`.

## Guía rápida

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
DETECTAR
↓
DECIDIR
↓
ACTUAR
↓
VERIFICAR
↓
CORREGIR / REINTENTAR
↓
NOTIFICAR
↓
REGISTRAR RESULTADO
```

## 3. Flujo funcional principal

```text
Ventas históricas
↓
Predicción de demanda
↓
Plan de producción
↓
Cálculo de ingredientes
↓
Detección de faltantes
↓
Generación de pedidos
↓
Envío a proveedores
↓
Verificación del envío
↓
Producción
↓
Ventas durante el día
↓
Detección de excedentes
↓
Promoción automática
↓
Verificación del efecto
↓
Registro del resultado
↓
Panel e informes
```

## 4. Alcance

FoodSave se centra en:
- planificación;
- automatización;
- abastecimiento;
- prevención de desperdicio;
- control;
- trazabilidad;
- seguimiento de resultados.

No debe convertirse en:
- ERP completo;
- POS completo;
- sistema contable;
- facturación electrónica;
- CRM;
- recursos humanos;
- delivery;
- ecommerce completo;
- sistema de pagos.

Estas áreas pueden existir como integraciones externas.


# 5. Arquitectura

## 5.1 Decisión arquitectónica

Se propone un **monolito modular con procesamiento asíncrono para automatizaciones**.

Ventajas:
- módulos funcionales bien delimitados;
- menor complejidad operativa;
- despliegue sencillo;
- integración directa entre dominios;
- posibilidad de trabajar en paralelo;
- posibilidad futura de extraer servicios.

## 5.2 Conjunto de tecnologías

### Interfaz
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts
- TanStack Query
- React Hook Form
- Zod

### Servidor
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Persistencia
- PostgreSQL

### Automatización
- Celery
- Redis
- Celery Beat

### Datos / predicción
- Pandas
- NumPy
- scikit-learn

### Seguridad
- JWT
- bcrypt / passlib

### Pruebas
- Pytest
- Playwright
- Vitest / React pruebas Library opcional

### Infraestructura
- Docker
- Docker Compose

### CI/CD
- GitHub Actions

### Diseño y documentación
- Figma
- OpenAPI / Swagger
- Markdown
- Mermaid

## 5.3 Arquitectura general

La interfaz se comunica con la API. El servidor guarda datos en PostgreSQL y envía trabajos a Redis para que Celery los procese. Celery Beat programa las ejecuciones periódicas.

```mermaid
flowchart LR
    U[Administrador] --> F[Aplicación web<br/>Next.js]
    F -->|REST / JSON| A[API<br/>FastAPI]
    A --> D[(PostgreSQL)]
    A --> R[(Redis)]
    R --> W[Trabajadores<br/>Celery]
    B[Celery Beat] --> R
    W --> D
    W --> P[Proveedores]
    W --> C[Canales de venta]
    W --> N[Servicio de notificaciones]
```

# 6. Vistas C4

## 6.1 Contexto

Personas y sistemas externos que interactúan con FoodSave.

```mermaid
flowchart LR
    administrador[Administrador del negocio] -->|Usa| foodsave[FoodSave]
    foodsave -->|Envía pedidos| proveedor[Proveedor]
    foodsave -->|Publica promociones| canal[Canal de venta]
    foodsave -->|Envía alertas| avisos[Servicio de notificaciones]
```

## 6.2 Contenedores

Aplicación web, API, trabajos asíncronos y almacenamiento.

```mermaid
flowchart LR
    administrador[Administrador]
    proveedor[Proveedor]
    canal[Canal de venta]
    avisos[Servicio de notificaciones]

    subgraph FoodSave
        interfaz[Aplicación web<br/>Next.js]
        api[API del servidor<br/>FastAPI]
        trabajador[Trabajos asíncronos<br/>Celery]
        base[(PostgreSQL)]
        cola[(Redis)]
    end

    administrador -->|Usa| interfaz
    interfaz -->|REST y JSON| api
    api -->|Lee y escribe| base
    api -->|Encola tareas| cola
    cola -->|Entrega tareas| trabajador
    trabajador -->|Lee y escribe| base
    trabajador -->|Envía pedidos| proveedor
    trabajador -->|Publica promociones| canal
    trabajador -->|Envía alertas| avisos
```

## 6.3 Componentes

Módulos principales del servidor.

```mermaid
flowchart LR
    api[API FastAPI]
    autenticacion[Autenticación]
    negocios[Negocios]
    productos[Productos]
    recetas[Recetas]
    ventas[Ventas]
    produccion[Producción]
    inventario[Inventario]
    pronosticos[Pronósticos]
    planificacion[Planificación]
    proveedores[Proveedores]
    compras[Compras]
    excedentes[Excedentes]
    promociones[Promociones]
    automatizaciones[Motor de automatización]
    informes[Informes]
    notificaciones[Notificaciones]

    api --> autenticacion
    api --> negocios
    api --> productos
    api --> recetas
    api --> ventas
    api --> produccion
    api --> inventario
    api --> pronosticos
    api --> planificacion
    api --> proveedores
    api --> compras
    api --> excedentes
    api --> promociones
    api --> automatizaciones
    api --> informes

    automatizaciones --> pronosticos
    automatizaciones --> planificacion
    automatizaciones --> compras
    automatizaciones --> excedentes
    automatizaciones --> promociones
    automatizaciones --> notificaciones
```

# 7. Módulos funcionales

## 7.1 Autenticación

**Responsable:** Axel Cueva.

Responsabilidades:
- inicio de sesión;
- renovación de la credencial de acceso;
- protección de rutas;
- roles.

Entidades:
- Usuario
- Rol

Roles iniciales:
- ADMINISTRADOR
- OPERADOR

## 7.2 Negocios

**Responsable:** Axel Cueva.

Entidad:
- negocio

Campos sugeridos:
- id
- nombre
- zona_horaria
- hora_apertura
- hora_cierre
- moneda
- creado_en
- actualizado_en

## 7.3 Productos

**Responsable:** Leonardo Vera.

Entidad:
- producto

Campos:
- id
- nombre
- categoria
- precio_venta
- costo_estimado
- activo
- creado_en
- actualizado_en

Funcionalidades:
- crear;
- editar;
- consultar;
- listar;
- filtrar;
- desactivar.

## 7.4 Ingredientes y recetas

**Responsable de ambos módulos:** Kevin Bohorquez.

Entidades:
- ingrediente
- receta
- IngredienteReceta

Ejemplo:
```text
Empanada de pollo
100 g pollo
80 g harina
30 g cebolla
```

Funcionalidades:
- registrar ingredientes;
- crear receta;
- editar receta;
- asociar ingredientes;
- definir cantidad por unidad.

## 7.5 Ventas

**Responsable:** Leonardo Vera.

Entidad:
- venta

Campos:
- id
- producto_id
- cantidad
- precio_unitario
- total
- fecha_venta
- hora_venta
- origen
- creado_en

Funcionalidades:
- registrar venta;
- consultar histórico;
- filtrar por fecha;
- filtrar por producto;
- importar CSV;
- agrupar ventas.

## 7.6 Producción

**Responsable:** Leonardo Vera.

Entidad:
- registro de producción

Campos:
- id
- producto_id
- fecha
- cantidad_planificada
- cantidad_producida
- creado_en

Funcionalidades:
- registrar producción;
- actualizar cantidad;
- comparar el plan con la cantidad producida;
- consultar historial.

## 7.7 Inventario

**Responsable:** Leonardo Vera.

Entidades:
- Inventario
- movimiento de inventario

Inventario:
- id
- ingrediente_id
- existencias_actuales
- unidad
- existencias_minimas
- actualizado_en

movimiento de inventario:
- id
- ingrediente_id
- tipo
- cantidad
- motivo
- creado_en

Tipos:
- ENTRADA
- SALIDA
- AJUSTE
- PRODUCCION
- DESPERDICIO

Funcionalidades:
- consultar existencias;
- registrar entrada;
- registrar salida;
- ajustar;
- detectar existencias bajas;
- consultar movimientos.


## 7.8 Pronósticos

**Responsable:** Kevin Bohorquez.

Responsabilidad:
- estimar demanda futura.

Entradas:
- ventas históricas;
- producto;
- día de semana;
- tendencia reciente.

Variables futuras:
- feriados;
- clima;
- promociones;
- temporada;
- eventos.

Entidad:
- pronóstico

Campos:
- id
- producto_id
- fecha_pronostico
- cantidad_pronosticada
- confianza
- nombre_modelo
- version_modelo
- creado_en

Método base:
```text
Promedio histórico por día de semana
+
media móvil
```

Métodos futuros:
- Random Forest
- Gradient Boosting
- XGBoost

## 7.9 Planificación

**Responsable:** Kevin Bohorquez.

Fórmula conceptual:

```text
Producción recomendada =
demanda prevista
-
existencias del producto terminado
+
margen de seguridad
```

Entidades:
- plan de producción
- elemento del plan de producción
- necesidad de ingredientes

plan de producción:
- id
- fecha_plan
- estado
- creado_en

elemento del plan de producción:
- id
- plan_produccion_id
- producto_id
- cantidad_pronosticada
- cantidad_existente
- cantidad_seguridad
- cantidad_recomendada

necesidad de ingredientes:
- id
- plan_produccion_id
- ingrediente_id
- cantidad_requerida
- cantidad_disponible
- cantidad_faltante

## 7.10 Proveedores

**Responsable:** Leonardo Aguirre.

Entidades:
- proveedor
- insumo del proveedor

proveedor:
- id
- nombre
- correo
- telefono
- medio_contacto_preferido
- activo
- creado_en

insumo del proveedor:
- proveedor_id
- ingrediente_id
- precio_unitario
- pedido_minimo
- plazo_entrega_estimado
- preferido

Funcionalidades:
- crear;
- actualizar;
- desactivar;
- asociar insumos;
- marcar proveedor habitual;
- registrar precio.

## 7.11 Compras

**Responsable:** Leonardo Aguirre.

Flujo:
```text
NecesidadIngrediente
↓
faltante > 0
↓
buscar proveedor
↓
agrupar insumos
↓
crear pedido
↓
enviar
↓
verificar
```

Entidades:
- pedido de compra
- elemento del pedido de compra

Estados:
- GENERADO
- PENDIENTE
- ENVIANDO
- ENVIADO
- CONFIRMADO
- REINTENTANDO
- FALLIDO
- CANCELADO

## 7.12 Excedentes

**Responsable:** Max Rojas.

Cálculo conceptual:
```text
existencias_restantes = producido - vendido

excedente_estimado =
existencias_restantes - ventas_estimadas_hasta_cierre
```

Entidad:
- detección de excedentes

Campos:
- id
- producto_id
- detectado_en
- existencias_actuales
- ventas_restantes_estimadas
- excedente_estimado
- nivel_riesgo
- estado

Riesgo:
- BAJO
- MEDIO
- ALTO
- CRITICO

## 7.13 Promociones

**Responsable:** Max Rojas.

Entidad:
- promoción

Campos:
- id
- producto_id
- deteccion_excedente_id
- porcentaje_descuento
- inicia_en
- termina_en
- estado
- creado_en

Estados:
- PROGRAMADO
- ACTIVO
- FINALIZADO
- CANCELADO
- FALLIDO

Regla ejemplo:
```text
SI nivel_riesgo = ALTO
Y tiempo_hasta_cierre <= 90 minutos
ENTONCES porcentaje_descuento = 10%
```


# 8. Automatización y control

**Responsable:** Axel Cueva.

## 8.1 Automatización

Campos:
- id
- tipo
- nombre
- habilitado
- programacion
- maximo_reintentos
- configuracion
- creado_en
- actualizado_en

Tipos:
- PLANIFICACION_DIARIA
- PEDIDO_PROVEEDOR
- SEGUIMIENTO_EXCEDENTES
- ACTIVACION_PROMOCION
- SEGUIMIENTO_PROMOCION

## 8.2 Ejecución de automatización

Campos:
- id
- automatizacion_id
- estado
- inicio_en
- fin_en
- datos_entrada
- datos_salida
- mensaje_error
- cantidad_reintentos

Estados:
- PENDIENTE
- EN_EJECUCION
- VERIFICANDO
- COMPLETADO
- REINTENTANDO
- FALLIDO
- CANCELADO

## 8.3 Intento de automatización

Campos:
- id
- ejecucion_automatizacion_id
- numero_intento
- inicio_en
- fin_en
- estado
- mensaje_error

## 8.4 Patrón de control

```text
ejecutar()
↓
verificar()
↓
¿correcto?

SI
↓
COMPLETADO

NO
↓
¿quedan reintentos?

SI
↓
REINTENTANDO
↓
ejecutar()

NO
↓
FALLIDO
↓
notificar()
```

## 8.5 Automatización — Planificación diaria

Disparador:
```text
22:00 todos los días
```

Flujo:
```text
leer ventas
↓
validar información
↓
generar pronóstico
↓
generar plan
↓
calcular ingredientes
↓
consultar inventario
↓
generar faltantes
↓
guardar resultado
```

Control:
```text
¿Plan generado correctamente?
NO → reintentar
nuevo fallo → registrar error → notificar
```

## 8.6 Automatización — Abastecimiento

```text
faltante > 0
↓
buscar proveedor
↓
agrupar necesidades
↓
crear pedido
↓
enviar
↓
verificar envío
```

Control:
```text
envío no confirmado
↓
reintentar
↓
si vuelve a fallar
FALLIDO
↓
notificar
```

## 8.7 Automatización — Control de excedentes

Disparador:
```text
cada 30 minutos
```

Flujo:
```text
leer producción
↓
leer ventas
↓
calcular existencias restantes
↓
predecir venta restante
↓
calcular excedente
↓
calcular riesgo
```

## 8.8 Automatización — Promoción preventiva

```text
riesgo detectado
↓
seleccionar estrategia
↓
calcular descuento
↓
crear promoción
↓
publicar
↓
verificar publicación
```

## 8.9 Automatización — Control de promoción

```text
esperar intervalo
↓
leer ventas nuevas
↓
recalcular excedente
↓
¿riesgo disminuyó?
```

Si sí:
```text
mantener / finalizar
```

Si no:
```text
recalcular acción
↓
ejecutar nueva promoción
```


# 9. Notificaciones

**Responsable:** Axel Cueva.

Entidad:
- notificación

Campos:
- id
- usuario_id
- tipo
- titulo
- mensaje
- leida
- creado_en

Canales iniciales:
- notificación interna;
- correo.

Posibles integraciones:
- WhatsApp;
- Slack;
- notificaciones móviles.

# 10. Informes

**Responsable:** Edu Sanchez.

Métricas:

## Operación
- producción;
- ventas;
- excedentes;
- existencias;
- pedidos.

## Predicción
- MAE;
- MAPE;
- precisión aproximada.

## Automatización
- ejecuciones;
- completadas;
- fallidas;
- reintentos;
- tiempo promedio.

## Impacto económico
- pérdida potencial;
- pérdida evitada;
- costo de desperdicio.

## Desperdicio
- unidades desperdiciadas;
- unidades recuperadas;
- kg desperdiciados;
- kg evitados.


# 11. Modelo conceptual de datos

Este diagrama muestra relaciones conceptuales; todavía no define tablas ni columnas definitivas.

```mermaid
erDiagram
    NEGOCIO ||--o{ USUARIO : tiene
    NEGOCIO ||--o{ PRODUCTO : posee
    NEGOCIO ||--o{ INGREDIENTE : posee
    NEGOCIO ||--o{ PROVEEDOR : trabaja_con

    PRODUCTO ||--|| RECETA : tiene
    RECETA ||--o{ RECETA_INGREDIENTE : contiene
    INGREDIENTE ||--o{ RECETA_INGREDIENTE : se_usa_en

    PRODUCTO ||--o{ VENTA : tiene
    PRODUCTO ||--o{ REGISTRO_PRODUCCION : tiene
    PRODUCTO ||--o{ PRONOSTICO : tiene

    INGREDIENTE ||--|| INVENTARIO : tiene
    INGREDIENTE ||--o{ MOVIMIENTO_INVENTARIO : tiene

    PLAN_PRODUCCION ||--o{ ELEMENTO_PLAN_PRODUCCION : contiene
    PRODUCTO ||--o{ ELEMENTO_PLAN_PRODUCCION : se_planifica

    PLAN_PRODUCCION ||--o{ NECESIDAD_INGREDIENTE : genera
    INGREDIENTE ||--o{ NECESIDAD_INGREDIENTE : se_necesita

    PROVEEDOR ||--o{ PROVEEDOR_INGREDIENTE : ofrece
    INGREDIENTE ||--o{ PROVEEDOR_INGREDIENTE : es_suministrado

    PROVEEDOR ||--o{ PEDIDO_COMPRA : recibe
    PEDIDO_COMPRA ||--o{ ELEMENTO_PEDIDO_COMPRA : contiene
    INGREDIENTE ||--o{ ELEMENTO_PEDIDO_COMPRA : se_solicita

    PRODUCTO ||--o{ DETECCION_EXCEDENTE : se_detecta
    DETECCION_EXCEDENTE ||--o{ PROMOCION : activa

    AUTOMATIZACION ||--o{ EJECUCION_AUTOMATIZACION : ejecuta
    EJECUCION_AUTOMATIZACION ||--o{ INTENTO_AUTOMATIZACION : reintenta
```

# 12. API propuesta

Base:
```text
/api/v1
```

## Autenticación
```http
POST /autenticacion/iniciar-sesion
POST /autenticacion/renovar
GET  /autenticacion/mi-perfil
```

## Negocios
```http
GET   /negocios/actual
PATCH /negocios/actual
```

## Productos
```http
GET    /productos
GET    /productos/{id}
POST   /productos
PUT    /productos/{id}
DELETE /productos/{id}
```

## Ingredientes
```http
GET    /ingredientes
GET    /ingredientes/{id}
POST   /ingredientes
PUT    /ingredientes/{id}
DELETE /ingredientes/{id}
```

## Recetas
```http
GET  /productos/{producto_id}/receta
POST /productos/{producto_id}/receta
PUT  /productos/{producto_id}/receta
```

## Ventas
```http
GET  /ventas
POST /ventas
POST /ventas/importar
GET  /ventas/resumen
```

## Producción
```http
GET  /produccion
POST /produccion
PUT  /produccion/{id}
```

## Inventario
```http
GET  /inventario
GET  /inventario/{ingrediente_id}
POST /inventario/movimientos
GET  /inventario/movimientos
GET  /inventario/existencias-bajas
```

## Pronósticos
```http
GET  /pronosticos
GET  /pronosticos/{fecha}
POST /pronosticos/ejecutar
```

## Planificación
```http
GET  /planes
GET  /planes/{id}
POST /planes/generar
GET  /planes/{id}/ingredientes
```

## Proveedores
```http
GET    /proveedores
GET    /proveedores/{id}
POST   /proveedores
PUT    /proveedores/{id}
DELETE /proveedores/{id}
POST   /proveedores/{id}/ingredientes
```

## Compras
```http
GET  /pedidos-compra
GET  /pedidos-compra/{id}
POST /pedidos-compra/generar
POST /pedidos-compra/{id}/enviar
POST /pedidos-compra/{id}/reintentar
```

## Excedentes
```http
GET  /excedentes
GET  /excedentes/actual
POST /excedentes/ejecutar
```

## Promociones
```http
GET  /promociones
GET  /promociones/{id}
POST /promociones/generar
POST /promociones/{id}/activar
POST /promociones/{id}/detener
```

## Automatizaciones
```http
GET  /automatizaciones
GET  /automatizaciones/{id}
PUT  /automatizaciones/{id}
GET  /ejecuciones-automatizacion
GET  /ejecuciones-automatizacion/{id}
POST /automatizaciones/{id}/ejecutar
POST /ejecuciones-automatizacion/{id}/reintentar
```

## Informes
```http
GET /informes/panel
GET /informes/operacion
GET /informes/desperdicio
GET /informes/pronosticos
GET /informes/automatizaciones
```


# 13. Estructura del repositorio

Cada subcarpeta contiene un `README.md` que describe su propósito. Esta es la estructura documental y de carpetas creada hasta ahora; los archivos de aplicación se añadirán durante la implementación.

```text
foodsave/
├── README.md
├── .gitignore
├── .env.example
├── docs/
│   ├── arquitectura/
│   │   ├── vision_general.md
│   │   ├── decisiones/
│   │   ├── c4/
│   │   └── diagramas/
│   ├── api/
│   ├── diseno/
│   ├── funcionalidades/
│   ├── base_de_datos/
│   ├── automatizacion/
│   └── equipo/
├── frontend/
│   ├── public/
│   └── src/
│       ├── app/
│       │   ├── iniciar-sesion/
│       │   ├── panel/
│       │   ├── productos/
│       │   ├── produccion/
│       │   ├── inventario/
│       │   ├── compras/
│       │   ├── proveedores/
│       │   ├── excedentes/
│       │   ├── promociones/
│       │   ├── automatizaciones/
│       │   ├── informes/
│       │   └── configuracion/
│       ├── components/
│       │   ├── ui/
│       │   ├── layout/
│       │   ├── panel/
│       │   ├── charts/
│       │   ├── tables/
│       │   ├── automatizacion/
│       │   └── forms/
│       ├── features/
│       │   ├── productos/
│       │   ├── ingredientes/
│       │   ├── recetas/
│       │   ├── ventas/
│       │   ├── produccion/
│       │   ├── inventario/
│       │   ├── planificacion/
│       │   ├── proveedores/
│       │   ├── compras/
│       │   ├── excedentes/
│       │   ├── promociones/
│       │   ├── desperdicio/
│       │   └── automatizaciones/
│       ├── services/
│       ├── hooks/
│       ├── types/
│       ├── utils/
│       └── constants/
├── backend/
│   ├── migrations/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   └── app/
│       ├── core/
│       ├── shared/
│       │   ├── enums/
│       │   ├── schemas/
│       │   ├── utils/
│       │   └── events/
│       ├── modules/
│       │   ├── autenticacion/
│       │   ├── negocios/
│       │   ├── productos/
│       │   ├── ingredientes/
│       │   ├── recetas/
│       │   ├── ventas/
│       │   ├── produccion/
│       │   ├── inventario/
│       │   ├── pronosticos/
│       │   ├── planificacion/
│       │   ├── proveedores/
│       │   ├── compras/
│       │   ├── excedentes/
│       │   ├── promociones/
│       │   ├── desperdicio/
│       │   ├── automatizaciones/
│       │   ├── notificaciones/
│       │   └── informes/
│       ├── workers/
│       │   ├── tasks/
│       │   └── retry/
│       └── integrations/
│           ├── proveedores/
│           ├── notificaciones/
│           └── canales_venta/
├── scripts/
└── .github/
    └── workflows/
```

`src/app`, `public`, `.github/workflows` y `README.md` conservan sus nombres porque Next.js, GitHub y las herramientas de documentación los reconocen así. Los nombres propios de tecnologías, como FastAPI y PostgreSQL, también se mantienen.

Cuando comience la implementación se incorporarán `package.json`, `pyproject.toml`, archivos Dockerfile, migraciones y flujos de integración continua con contenido funcional. En Next.js, `layout.tsx` y `page.tsx` son nombres reservados y deberán conservarse. Los archivos propios del servidor pueden usar nombres en español, como `principal.py`, `rutas.py` y `servicio.py`.

# 14. Estructura interna de cada módulo del servidor

```text
modulo/
├── rutas.py
├── servicio.py
├── repositorio.py
├── modelos.py
├── esquemas.py
├── dependencias.py
├── errores.py
└── tests/
```

Responsabilidades:

- `rutas.py`: recibe solicitudes HTTP, valida parámetros y delega en el servicio.
- `servicio.py`: implementa reglas de negocio y coordina operaciones del módulo.
- `repositorio.py`: realiza consultas y operaciones de persistencia.
- `modelos.py`: define modelos de SQLAlchemy.
- `esquemas.py`: define esquemas de Pydantic.
- `dependencias.py`: reúne dependencias del módulo.
- `errores.py`: define errores propios del dominio.
- `tests/`: comprueba reglas de negocio y rutas.

Un módulo no accede directamente al repositorio de otro. Por ejemplo, planificación debe solicitar las existencias al servicio de inventario.

# 15. Contratos entre módulos

## Planificación → Pronósticos

```python
servicio_pronosticos.obtener_pronostico(producto_id, fecha)
```

Respuesta:
```json
{
  "producto_id": 1,
  "fecha": "2026-09-24",
  "cantidad_pronosticada": 60,
  "confianza": 0.93
}
```

## Planificación → Inventario

```python
servicio_inventario.obtener_existencias(ingrediente_id)
```

Respuesta:
```json
{
  "ingrediente_id": 5,
  "existencias": 2,
  "unidad": "kg"
}
```

## Planificación → Compras

```json
{
  "ingrediente_id": 5,
  "requerido": 5.8,
  "disponible": 2,
  "faltante": 3.8
}
```

## Compras → Proveedores

```python
servicio_proveedores.buscar_proveedor_preferido(ingrediente_id)
```

## Excedentes → Promociones

```json
{
  "producto_id": 1,
  "existencias_actuales": 24,
  "ventas_estimadas": 9,
  "excedente_estimado": 15,
  "riesgo": "ALTO"
}
```


# 16. División del equipo

Los módulos funcionales se reparten entre las seis personas. Una persona puede encargarse de varios módulos relacionados; **cada módulo tiene un único responsable de interfaz, servidor, API, pruebas e integración**. Los componentes compartidos tienen una persona coordinadora, pero los cambios de cada dominio siguen siendo responsabilidad de su dueño.

| Responsable | Módulos asignados | Alcance integrado |
|---|---|---|
| Axel Cueva | Autenticación; Negocios y configuración; Automatizaciones y control; Notificaciones | Acceso por negocio, preferencias, programación, ejecuciones, reintentos y avisos |
| Edu Sanchez | Panel principal; Informes | Indicadores, consultas agregadas, visualizaciones y componentes de interfaz compartidos |
| Kevin Bohorquez | Ingredientes; Recetas; Pronósticos; Planificación | Catálogo de ingredientes, composición de productos, demanda prevista, planes y faltantes |
| Leonardo Vera | Productos; Ventas; Producción; Inventario | Catálogo de productos, datos operativos, existencias y movimientos |
| Leonardo Aguirre | Proveedores; Compras | Oferta de insumos, selección de proveedor, pedidos, envíos y confirmaciones |
| Max Rojas | Excedentes; Promociones; Desperdicio | Detección de riesgo, acciones preventivas, medición y merma real |

Esta tabla cubre todos los módulos de la sección 7 y los módulos de automatización, notificaciones e informes. **Configuración** forma parte de Negocios y configuración; **ejecuciones y recuperación** forman parte de Automatizaciones y control. Las dependencias entre responsables se coordinan mediante contratos, sin trasladar la propiedad de un módulo.

## Responsabilidades comunes

- **Interfaz:** crear las pantallas, formularios y visualizaciones de su módulo, con validaciones y estados de carga, error y ausencia de datos.
- **Servidor:** implementar reglas de negocio, persistencia, modelos y migraciones de su módulo.
- **API:** diseñar, implementar y documentar las rutas de su módulo y conectarlas con su interfaz.
- **Calidad:** probar el módulo, aplicar los permisos por negocio y documentar su uso.
- **Integración:** acordar contratos con los demás responsables y entregar su funcionalidad completa, desde la interfaz hasta la base de datos.

## Axel Cueva — Autenticación, negocios, automatización y notificaciones

- **Interfaz:** acceso, configuración del negocio, automatizaciones, historial de ejecuciones, errores, reintentos y notificaciones.
- **Servidor:** autenticación, permisos por negocio, reglas de configuración, programación y ejecución de tareas, verificación, reintentos, eventos y avisos; configuración de Redis, Celery y Celery Beat.
- **API:** autenticación, negocios y configuración, automatizaciones, ejecuciones, reintentos y notificaciones.
- **Integración:** orquestar los servicios de los demás módulos mediante contratos acordados y coordinar la arquitectura general.

## Edu Sanchez — Panel principal e informes

- **Interfaz:** panel de control, filtros, indicadores, tablas y gráficos; coordinación de la estructura visual y los componentes compartidos.
- **Servidor:** consultas y agregaciones para métricas operativas, de predicción, automatización, impacto económico y desperdicio.
- **API:** rutas del panel y los informes, con filtros y respuestas adecuadas para las visualizaciones.
- **Integración:** obtener datos de los demás módulos y presentar resultados consolidados.

## Kevin Bohorquez — Ingredientes, recetas, predicción y planificación

- **Interfaz:** ingredientes, recetas, pronósticos, métricas de predicción, planes de producción y necesidades de insumos.
- **Servidor:** catálogo de ingredientes, composición de recetas, preparación de datos, predicción de demanda, planes y cálculo de ingredientes.
- **API:** ingredientes, recetas, pronósticos, planes y necesidades de insumos.
- **Integración:** utilizar ventas, recetas e inventario; entregar faltantes al módulo de compras y permitir la planificación automática.

## Leonardo Vera — Productos, ventas, producción e inventario

- **Interfaz:** productos, ventas, importación de archivos CSV, producción, existencias y movimientos de inventario.
- **Servidor:** catálogo de productos, registro de ventas y producción, importación de datos, existencias y movimientos.
- **API:** productos, ventas, producción e inventario; importación CSV y movimientos.
- **Integración:** proporcionar datos operativos a predicción, planificación, excedentes e informes.

## Leonardo Aguirre — Proveedores y compras

- **Interfaz:** proveedores, insumos suministrados, precios, pedidos y seguimiento de estados y envíos.
- **Servidor:** selección de proveedores, generación y envío de pedidos, precios y gestión de estados.
- **API:** gestión de proveedores e insumos, generación y consulta de pedidos, envío y reintento de pedidos.
- **Integración:** recibir faltantes de planificación y conectar el abastecimiento con las automatizaciones.

## Max Rojas — Excedentes, promociones y desperdicio

- **Interfaz:** excedentes, niveles de riesgo, promociones, seguimiento de resultados y registro de desperdicio.
- **Servidor:** detección y clasificación de excedentes, reglas de promoción, activación, seguimiento, desperdicio y métricas del módulo.
- **API:** consulta de excedentes, generación y gestión de promociones, registro y consulta de desperdicio.
- **Integración:** utilizar ventas y producción, conectar las acciones preventivas con las automatizaciones y proporcionar resultados a informes.

## Coordinación de elementos compartidos

- Axel coordina arquitectura, contratos, infraestructura base e integración general; cada persona implementa y verifica la integración de sus módulos.
- Edu coordina la estructura visual y los componentes compartidos; cada persona construye las pantallas de sus módulos con esa base.
- Autenticación y negocios pertenecen a Axel; productos, a Leonardo Vera; ingredientes y recetas, a Kevin. Se consulta al dueño antes de cambiar contratos compartidos.
- La responsabilidad integral definida aquí prevalece sobre las listas antiguas de entregables por capas de otras secciones.

# 17. Dependencias del equipo

**Planificación y abastecimiento:** Leonardo Vera entrega ventas e inventario a Kevin Bohorquez; Kevin genera pronósticos, planes y faltantes para Leonardo Aguirre; Leonardo gestiona proveedores y compras; Axel coordina la ejecución automática y el control.

**Prevención de excedentes:** Leonardo Vera entrega ventas y producción a Max Rojas; Max detecta excedentes y gestiona promociones; Axel coordina la automatización y sus reintentos.

**Visualización:** cada responsable desarrolla las pantallas de su módulo. Edu coordina la estructura visual compartida y construye el panel y los informes con los datos de los demás módulos.

# 18. Entregables por persona

Cada entrega incluye interfaz, lógica del servidor, rutas de la API, pruebas y documentación de su módulo:

- **Axel:** autenticación, negocios y configuración, automatizaciones, control, reintentos, notificaciones e integración general.
- **Edu:** panel de control, informes, visualizaciones y componentes compartidos.
- **Kevin:** ingredientes, recetas, pronósticos, planes de producción y faltantes.
- **Leonardo Vera:** productos, ventas, producción, inventario e importación de archivos CSV.
- **Leonardo Aguirre:** proveedores, pedidos, envíos y seguimiento de estados.
- **Max:** excedentes, promociones, seguimiento y desperdicio.

La [sección 16](#16-división-del-equipo) detalla las responsabilidades.

# 19. Flujo de trabajo con Git

Cada integrante trabaja en una rama permanente con su apellido en minúsculas: `cueva`, `sanchez`, `bohorquez`, `vera`, `aguirre` y `rojas`. `main` conserva la versión estable. La descripción completa y los comandos están en [flujo-git.md](docs/equipo/flujo-git.md).

Para crear una rama desde la versión actual de `main` y publicarla:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c cueva
git push -u origin cueva
```

Repite el último par de comandos con el apellido correspondiente. Cada integrante sube sus cambios a su rama, solicita revisión y la integra a `main` cuando las pruebas y la revisión estén completas.

Convención de mensajes de cambios:

```text
funcion(inventario): agregar movimiento de existencias
correccion(compras): evitar pedidos duplicados
prueba(automatizacion): verificar politica de reintentos
```

Cada solicitud debe incluir descripción, módulo afectado, forma de probarlo, dependencias y capturas si aplica. Antes de incorporarla, deben pasar las pruebas y el análisis estático, recibir aprobación de revisión y no tener conflictos.

# 20. Orden de construcción

1. **Base técnica:** estructura del repositorio, Docker, FastAPI, Next.js, PostgreSQL, Redis, Celery, autenticación y configuración.
2. **Datos base:** negocios, productos, recetas, ingredientes y proveedores.
3. **Operación:** ventas, producción e inventario.
4. **Inteligencia:** pronósticos, planificación y necesidades de ingredientes.
5. **Abastecimiento:** compras, selección de proveedores y envío de pedidos.
6. **Prevención:** excedentes, promociones y desperdicio.
7. **Automatización:** programación, ejecución, verificación, reintentos y notificaciones.
8. **Visualización:** panel de control, informes e historial de automatizaciones.
9. **Integración:** flujos completos, pruebas, manejo de errores y observabilidad.

# 21. Flujos de extremo a extremo

## Planificación y abastecimiento

```text
Venta → Pronóstico → Plan de producción → Necesidades de ingredientes
→ Inventario → Faltantes → Proveedor → Pedido de compra
→ Ejecución automática → Envío → Verificación → Resultado
```

## Excedentes

```text
Producción + Ventas → Existencias restantes → Detección de excedente
→ Nivel de riesgo → Promoción → Ejecución automática
→ Publicación → Espera → Medición → Nuevo cálculo
```

# 22. Política de reintentos

La configuración inicial permite dos reintentos después del primer intento fallido (`maximo_reintentos = 2`). Cada fallo debe quedar registrado.

**Decisión de producto pendiente:** la pantalla de ejecución expresa «2 de 2» intentos y la configuración rotula «Intentos de reenvío: 2». Antes de implementar el contador y los reenvíos, el equipo debe acordar si el límite indica intentos totales o reintentos adicionales y unificar interfaz, API y regla del servidor.

```text
Primer intento → Fallo → Segundo intento → Fallo → Tercer intento
→ Fallo definitivo → Notificación
```

# 23. Registro de eventos

Cada automatización debe registrar la fecha y hora, su identificador, el identificador de ejecución, el número de intento, el estado, la duración, el error y el resultado. Estos datos permiten reconstruir qué ocurrió y por qué.

Los nombres concretos de campos se definirán al implementar el formato de los registros.

# 24. Observabilidad funcional

El sistema debe permitir consultar:
- qué automatización se ejecutó;
- cuándo;
- qué datos recibió;
- qué decidió;
- qué acción realizó;
- si funcionó;
- cuántas veces reintentó;
- qué error ocurrió.


# 25. Seguridad

Servidor:
- JWT;
- hash de contraseñas;
- autorización por negocio;
- validación Pydantic;
- protección de secretos;
- CORS;
- limitación de solicitudes en una fase futura.

La API se expone solo en la computadora local durante el desarrollo. El acceso a operaciones requiere autenticación y los datos de otro comercio permanecen en otra instalación y base de datos.

# 26. Variables de entorno

```text
ENTORNO_APLICACION=
URL_BASE_DATOS=
URL_REDIS=
JWT_SECRETO=
JWT_ALGORITMO=
DURACION_TOKEN_ACCESO_MINUTOS=
SMTP_SERVIDOR=
SMTP_PUERTO=
SMTP_USUARIO=
SMTP_CONTRASENA=
URL_INTERFAZ=
```

Nunca subir secretos al repositorio.

# 27. Docker Compose

Servicios previstos:

```text
interfaz
servidor
postgres
redis
trabajador-celery
planificador-celery
```

# 28. Pruebas

## Pruebas unitarias

- predicción de demanda;
- planificación de producción;
- movimientos de inventario;
- selección de proveedores y pedidos;
- detección de excedentes;
- promociones;
- ejecución y reintentos de automatizaciones.

## Pruebas de integración

Comprobar, por ejemplo, el flujo de registro de venta, generación de pronóstico y creación del plan.

## Pruebas de extremo a extremo

Ejecutar los flujos principales desde la interfaz.

# 29. Integración continua

Para el servidor y la interfaz, el flujo debe instalar dependencias, ejecutar análisis estático y pruebas y comprobar la compilación. Las comprobaciones concretas se incorporarán cuando exista una aplicación ejecutable.

# 30. Convenciones API

Respuesta:
```json
{
  "datos": {},
  "metadatos": {}
}
```

Error:
```json
{
  "error": {
    "codigo": "INVENTARIO_INSUFICIENTE",
    "mensaje": "Existencias insuficientes"
  }
}
```

Códigos de dominio sugeridos:
- PROVEEDOR_NO_ENCONTRADO
- INVENTARIO_INSUFICIENTE
- DATOS_PRONOSTICO_INSUFICIENTES
- AUTOMATIZACION_FALLIDA
- PROMOCION_YA_ACTIVA

Versionado:
```text
/api/v1
```


# 31. Reglas internas

1. Las rutas no contienen lógica compleja.
2. Los servicios contienen las reglas de negocio.
3. Los repositorios manejan la persistencia.
4. Un módulo no accede directamente al repositorio de otro.
5. El motor de automatización coordina los servicios.
6. No se duplica lógica.
7. Toda operación automática debe ser trazable.
8. Toda acción externa debe verificarse.
9. Todo fallo debe tener una política de control.
10. Todo contrato debe documentarse.

# 32. Nomenclatura

Servidor:
```text
snake_case
```

Clases:
```text
PascalCase
```

Interfaz:
```text
camelCase
```

Componentes:
```text
PascalCase
```

Rutas:
```text
kebab-case
```


# 33. Panel principal

**Responsable:** Edu Sanchez.

Debe responder:
- ¿Qué está pasando hoy?
- ¿Qué está automatizando FoodSave?
- ¿Qué salió mal?
- ¿Qué riesgo existe?
- ¿Qué ahorro se consiguió?

KPIs:
- demanda prevista;
- producción planificada;
- excedente esperado;
- pedidos enviados;
- promociones activas;
- automatizaciones completadas;
- automatizaciones fallidas;
- pérdida evitada.

Estados visibles:
- PENDIENTE
- EN_EJECUCION
- VERIFICANDO
- COMPLETADO
- REINTENTANDO
- FALLIDO

Mostrar:
- hora;
- acción;
- estado;
- intentos;
- resultado.


# 34. Arquitectura futura

La estructura modular permite extraer servicios posteriormente.

Ejemplos:

```text
Pronósticos
↓
Servicio de predicción
```

```text
Notificaciones
↓
Servicio de notificaciones
```

```text
Automatizaciones
↓
Servicio de flujos de trabajo
```

La separación futura debe hacerse solo cuando exista una necesidad real de escalabilidad, despliegue independiente o aislamiento.

# 35. Resultado esperado

FoodSave debe ser capaz de:

1. obtener datos;
2. analizar;
3. detectar una necesidad;
4. tomar una decisión;
5. ejecutar una acción;
6. verificar el resultado;
7. reintentar ante fallos;
8. notificar si no puede resolverlo;
9. registrar todo el proceso;
10. utilizar los resultados para nuevos análisis.

# 36. Resumen de responsabilidades

Cada persona entrega su módulo completo: interfaz, servidor y rutas de la API.

| Persona | Módulo |
|---|---|
| Axel Cueva | Autenticación; negocios y configuración; automatizaciones y control; notificaciones |
| Edu Sanchez | Panel principal; informes |
| Kevin Bohorquez | Ingredientes; recetas; pronósticos; planificación |
| Leonardo Vera | Productos; ventas; producción; inventario |
| Leonardo Aguirre | Proveedores; compras |
| Max Rojas | Excedentes; promociones; desperdicio |

# 37. Decisión técnica consolidada

```text
Interfaz
Next.js + TypeScript

Servidor
FastAPI + Python

Base de datos
PostgreSQL

Automatizaciones
Celery + Redis + Celery Beat

Datos y aprendizaje automático
Pandas + scikit-learn

Infraestructura
Docker + Docker Compose

CI
GitHub Actions
```

Arquitectura:

```text
Monolito modular
+
Trabajadores asíncronos
+
Programador
+
Automatización trazable
+
Verificación
+
Reintentos
+
Notificaciones
```

Flujo central:

```text
DATOS
↓
PREDICCIÓN
↓
PLANIFICACIÓN
↓
ABASTECIMIENTO
↓
OPERACIÓN
↓
DETECCIÓN DE EXCEDENTE
↓
ACCIÓN PREVENTIVA
↓
CONTROL
↓
REPORTES
```

# 38. Especificaciones de producto

La [especificación integral de diseño](documentacion/diseno/especificacion-visual.md) define identidad, colores, tipografía, componentes, composición, estados, accesibilidad y estructura de las pantallas. La [especificación funcional](documentacion/funcionalidades/especificacion-modulos.md) describe objetivo, información, acciones, estados y límites de cada sección del producto. Ambas pueden leerse de forma independiente. Las [referencias visuales conservadas](documentacion/diseno/mockups/README.md) se mantienen separadas de las especificaciones.

# 39. Cronograma del proyecto

El plan usa semanas académicas y evita asignar fechas de calendario no confirmadas. Las semanas 1 a 3 son hitos comunicados por el equipo; la semana 5 es la semana actual y contempla presentar el avance del repositorio. El contenido de la semana 4 debe validarse con el equipo. Las semanas 6 a 16 son objetivos propuestos para seis responsables que trabajan **en paralelo por módulos completos**: interfaz, servidor, API, pruebas e integración.

| Semana | Objetivo | Entregable o criterio de aceptación | Estado |
|---|---|---|---|
| 1 | Presentar la idea del proyecto | Problema, público objetivo y propuesta FoodSave explicados | Realizado según el equipo |
| 2 | Presentar el flujo del sistema | Secuencia desde datos y predicción hasta prevención y control | Realizado según el equipo |
| 3 | Presentar la propuesta de interfaz | Pantallas principales y sistema visual expuestos | Realizado según el equipo |
| 4 | Consolidar alcance, arquitectura y responsabilidades | Acuerdos técnicos y distribución de todos los módulos; confirmar qué se entregó realmente esa semana | Por confirmar |
| 5 | Presentar el avance del repositorio | Estructura de carpetas, README principal, especificaciones, cronograma y distribución de responsabilidades | Semana actual; presentación prevista |
| 6 | Crear la base ejecutable común | Interfaz y API arrancan localmente; PostgreSQL conectado; migración inicial; autenticación y negocio mínimos; contratos entre responsables acordados | Propuesto |
| 7 | Implementar el primer corte de cada dominio | Productos, ingredientes, recetas, ventas, inventario y proveedores tienen datos y API básicos; pronóstico, plan, pedido, riesgo, panel y ejecución cuentan con un primer recorrido conectado | Propuesto |
| **8** | **Presentar la versión preliminar integrada** | **Se puede recorrer con un negocio de demostración: registrar o cargar datos, generar demanda y plan, detectar faltantes, crear un pedido, visualizar riesgo y una acción preventiva, y ver el resultado en el panel. La interfaz usa rutas reales y persistencia; las integraciones externas aún pueden usar adaptadores de prueba claramente identificados.** | **Hito propuesto** |
| 9 | Completar la operación diaria | Validaciones e importación de ventas, registro de producción, movimientos de inventario, catálogo y recetas; pruebas de consistencia de existencias | Propuesto |
| 10 | Completar planificación y abastecimiento | Pronóstico evaluable, plan revisable y aprobable, cálculo de faltantes, selección de proveedor, envío de pedido y estados de confirmación | Propuesto |
| 11 | Completar prevención de desperdicio | Detección y clasificación de excedentes, promociones dentro de límites, medición posterior y registro de desperdicio real | Propuesto |
| 12 | Completar automatización y recuperación | Programación, disparadores, trazabilidad, verificación, reintentos, manejo de duplicados y notificaciones ante fallos | Propuesto |
| 13 | Consolidar panel, informes y configuración | Indicadores con periodos y origen, métricas de impacto, filtros necesarios, límites y preferencias editables, permisos por negocio | Propuesto |
| 14 | Integrar y probar el ciclo completo | Pruebas de extremo a extremo para planificación, compra, excedente y fallo; conexiones disponibles verificadas; registros y observabilidad funcional | Propuesto |
| 15 | Estabilizar la entrega | Corrección de defectos, pruebas de regresión y seguridad, revisión de accesibilidad, documentación de instalación y preparación de demostración | Propuesto |
| **16** | **Entregar el sistema completo** | **Todos los módulos asignados funcionan integrados, con interfaz, API, persistencia, permisos, automatizaciones, pruebas y documentación; se demuestra el flujo normal y al menos un fallo recuperado, y se entrega una versión instalable.** | **Hito final propuesto** |

## Seguimiento

La versión preliminar de la semana 8 no equivale al sistema final: demuestra el recorrido principal con datos persistidos y deja visibles las integraciones externas simuladas. Las semanas 9 a 15 completan reglas, excepciones, mediciones, seguridad y calidad sin detener el trabajo paralelo. El equipo debe registrar evidencia de cada entrega —demostración, pruebas y cambios en el repositorio— antes de marcarla como realizada. Si una integración externa exige credenciales o acceso de un tercero, se debe documentar su estado y conservar un adaptador verificable para la demostración; no se presentará como conexión real algo que esté simulado.
