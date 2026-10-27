# Operación integrada: Docker, prueba pública y configuración remota

Ampliación autorizada expresamente el 27-10-2026. Codex implementa por solicitud del usuario; Cueva coordina, sin cambiar responsables. [Contrato](api/contrato-operacion-integrada.md). Evidencia real y límites en [Cueva](equipo/avances/cueva.md).

## Flujo implementado

1. Carga → preparación real del modelo → evaluación histórica. No se inventa un modelo listo ni se cambia la ventana de inferencia a hoy.
2. Programación → pronóstico → plan inmutable → necesidades → pedidos. Generar plan/pedido no mueve stock.
3. **Operación diaria → Producción:** seleccionar plan/producto, unidades realmente fabricadas y caducidad. Tandas hasta el pendiente; receta conservada del plan. Consumo FEFO de ingredientes y alta del lote terminado en una transacción. Una clave repetida no vuelve a consumir.
4. Pedido con aprobación manual o modo automático. Si `HABILITAR_ENLACES_PROVEEDOR=1`, los mensajes nuevos incluyen un enlace privado de respuesta de una hora real. Los mensajes ya reservados no se reescriben.
5. Proveedor: GET solo consulta; POST acepta/rechaza e indica entrega comprometida. No se usa DNI como contraseña ni se da acceso al panel. Respuesta, envío y recepción son estados separados. Sin respuesta al vencer → aviso administrativo. No se reenvía a ciegas si Telegram deja resultado incierto.
6. **Recepciones:** lista pedidos y respuesta del proveedor; solo aceptados/enviados permiten confirmar llegada. Ingredientes precargados, controles −/+ entre cero y pendiente, fecha, caducidad y descripción. Solo lo aceptado aumenta stock; una entrega incompleta/defectuosa conserva incidencia y avisa al administrador. Cero no crea movimiento.
7. **Notificaciones:** bandeja compartida administrativa persistente. Marcar leído no resuelve. El administrador contacta al proveedor fuera del sistema y registra la resolución interna; no se genera reposición ni nueva compra automáticamente.
8. Registrar otras tandas del mismo plan usando los ingredientes recibidos. Comprar/recibir no fabrica automáticamente.
9. **Ventas:** registro interno → salida FEFO de productos terminados y revisión de Ventas/reevaluación, sin consumir ingredientes otra vez. La tienda guarda sus ventas aparte de Ventas/ML, conforme ADR-009.
10. **Configuración:** productos seleccionados, reloj actual o escenario. Beat invoca control cada 30 s; la fecha durable de próxima revisión limita la evaluación de promociones a cada 600 s. Lee stock vigente sin exigir ajuste manual nuevo. La regla de descuento debe estar habilitada en Promociones.
11. Guarda sugerencia o motivo; evita duplicar pendientes/activas por lote/día. Admin aprueba/rechaza; solo aprobadas aparecen en catálogo/cotización. Mezcla de lotes con/sin descuento y finalización por agotamiento/vencimiento. Pagos siempre simulados; tarjeta nunca llega a la API.
12. Evaluación compara pronóstico con revisiones de ventas conocidas. Ausencia no es cero. Métricas no prueban ahorro/desperdicio reducido ni disparan reentrenamiento por sí solas.

## Páginas y permisos

| Persona | Acceso |
|---|---|
| Admin | Panel habitual, `/operaciones`, configuración/precios/aprobación y `/notificaciones`. |
| Operador | Mismo panel; registra producción, venta y recepción. Permisos administrativos denegados por servidor. |
| Cliente | `/tienda`: catálogo, carrito y pedidos propios persistidos. Google real configurado o cuenta local real habilitada para pruebas. |
| Proveedor | `/proveedor/pedido/<token>`, limitado a un pedido sin sesión administrativa. |

Los desplegables del menú tienen sangría y tono propio para distinguir opciones hijas. El estado activo conserva contraste y teclado.

## Arranque gratuito local

Docker Desktop con motor Linux activo y Compose v2.24.4+ (`!override`). Ejecutar desde la raíz:

```powershell
.\iniciar-demo.cmd
```

Crea `.env.pruebas` solo si falta: toma las tres cuentas públicas de `datos_carga/cuentas_demo.json` y genera claves independientes para PostgreSQL/JWT. Construye y arranca el proyecto **foodsave_pruebas** con base y volúmenes propios, sin modificar la instalación habitual. La web espera el chequeo saludable de la API y PostgreSQL antes de iniciar. Web `http://localhost:3100`; API de diagnóstico `http://localhost:8100`. Navegador y teléfono usan `/api/v1` a través de Next, sin URLs privadas de Docker.

La semilla v2 crea **12 productos en seis categorías, 16 insumos, recetas multingrediente y tres proveedores ficticios sin chat**. Nueve meses de ventas sintéticas de 2026 incluyen perfiles semanales distintos, tendencia, campañas ficticias, cero explícito y una ausencia deliberada que no se rellena. Reserva entrenamiento CatBoost real para el worker. Se consulta en Pronósticos/Automatizaciones. Fecha operativa de prueba **2026-09-29, 17:15**; no confundir lotes del escenario con stock vigente hoy. No se crean recibos Telegram falsos ni se envían mensajes. Configurar canal real y autorizar una prueba específica antes de transmitir.

### Escenarios para una exposición más completa

- Ciabatta y rollos: excedente del día para evaluar una sugerencia de promoción; aprobar sigue siendo una decisión del administrador.
- Brioche y pie de limón: últimas unidades. Tartaleta de fresas: agotada por stock cero. Quiche: hay ocho porciones físicas de un lote vencido, excluidas de la tienda.
- Keke y cheesecake: varios lotes con fechas distintas para observar FEFO y distinguir excedentes de lotes frescos.
- Mantequilla/queso con saldo limitado y fresas con cero conocido: producen faltantes al calcular el plan. Los tres proveedores están sin chat verificado; se muestra el bloqueo real, sin fingir pedidos aceptados o entregados.

[Referencia CSV de los doce productos](../datos_carga/demo_escenarios_v2.csv): saldos iniciales de una base nueva, no plantilla de importación ni estado actual después de ventas. Las cantidades de receta son ilustrativas, no fichas técnicas comerciales.

Al ejecutar la semilla sobre la demo v1 se amplía una sola vez mediante un marcador versionado. Conserva contraseñas, pedidos, planes, ventas previas y saldos ya consumidos; no reemplaza fichas/recetas editadas por el usuario. Crea versiones nuevas de las recetas originales y añade lotes e historia para los productos nuevos. Espera si hay entrenamiento activo; con un modelo anterior listo reserva otro entrenamiento/evaluación real para el catálogo ampliado. Los artefactos y pronósticos anteriores se conservan.

```powershell
.\iniciar-demo.cmd -NoBuild
.\iniciar-demo.cmd -Preparar
```

`-NoBuild` reutiliza imágenes; usar build después de cambiar código. `-Preparar` solo genera configuración privada, sin arrancar Docker. La semilla no restablece saldos ni contraseñas al repetir y se niega a sobrescribir una base ajena con datos.

## Cuentas

### Recorrido breve de la demo

1. Abrir `/iniciar-sesion` con la cuenta administrativa de la tabla siguiente. En `/operaciones`, comprobar la fecha de escenario `2026-09-29`.
2. En **Producción**, seleccionar el plan disponible, un producto con pendiente y una unidad; confirmar con caducidad igual o posterior al escenario. Revisar el movimiento en Inventario y el registro en Últimas operaciones.
3. En **Ventas**, registrar una unidad de ese producto. Baja el producto terminado; los ingredientes no se descuentan de nuevo.
4. En **Configuración**, revisar los productos vigilados; en **Promociones**, usar Revisar ahora para la presentación o esperar el ciclo de diez minutos. Aprobar una sugerencia pendiente. Las ya aprobadas se muestran en la tienda.
5. Abrir `/tienda/menu` en otra ventana, entrar con la cuenta cliente, agregar un producto, completar datos sintéticos y confirmar con pago simulado. Consultar **Mis pedidos**; la compra reduce stock sin agregarse a Ventas/ML.
6. Proveedor y recepción requieren un pedido enviado real a un chat propio de pruebas y aceptado mediante su enlace. La semilla no inventa ese envío: configurar el bot/chat antes de presentar ese tramo. La suite de integración cubre aceptación, vencimiento y recepción parcial con transporte de prueba; no acredita un Telegram real.

| Rol | Correo | Acceso |
|---|---|---|
| Admin | `admin.foodsave@example.com` | `/iniciar-sesion` |
| Trabajador | `operador.foodsave@example.com` | `/iniciar-sesion` |
| Cliente | `cliente.foodsave@example.com` | Cuenta local en `/tienda` |

**Correos y contraseñas de demo publicados por solicitud expresa del usuario:** [cuentas_demo.json](../datos_carga/cuentas_demo.json). Son los tres accesos de la demo actual y los valores iniciales para nuevas instalaciones. Son públicos y exclusivos para datos ficticios. El archivo no contiene claves PostgreSQL/JWT ni tokens Telegram.

Los datos mock también están versionados: [semilla operativa](../backend/app/modules/operaciones/semilla.py) y [catálogo/escenarios v2](../backend/app/modules/operaciones/semilla_catalogo.py). Cada compañero ejecuta `iniciar-demo.cmd` para crear su base independiente con el mismo origen y las mismas cuentas iniciales; no debe copiar una base privada ni su archivo `.env`.

### Alcance del checkout

La interfaz ofrece tarjeta, Yape y Plin **simulados**. No hay SDK, API ni webhook de una pasarela financiera: la API registra un pago de prueba aprobado con referencia `SIM-<id>`. La tarjeta se valida solo en el navegador y no se envía ni persiste. Checkout y detalle lo rotulan como simulación; no efectuar transferencias ni cargos reales. Esto no cambia por ampliar los datos mock.

`.tmp/credenciales-pruebas.txt` es una copia local de los accesos y `.env.pruebas` sigue fuera de Git por sus secretos de instalación. Si la instalación ya tenía otras contraseñas, el lanzador y la semilla las conservan; el archivo público no las cambia automáticamente. Cliente local verifica hash real, solo si `HABILITAR_CLIENTE_LOCAL=1`; no suplanta Google.

## Página pública gratuita

**Recuperación 27-10-2026, 09:37 America/Bogota:** tras apagar la laptop se recuperaron los servicios y los datos con `iniciar-demo.cmd -Publico -NoBuild`. La URL cambia al volver a iniciar el túnel; consultar `.tmp/url-publica.txt` y no reutilizar direcciones antiguas. Se comprobaron HTTPS/catálogo público sin credenciales y el flujo autenticado en localhost, con dos pedidos anteriores conservados y sin duplicar operaciones. Evidencia y límites de esta recuperación en la bitácora de Cueva.

**27-10-2026: publicación autorizada y verificada.** Tras el bloqueo inicial de revisión automática, el usuario autorizó expresamente exponer **toda la web y la API de esta demo**, incluido el inicio de sesión del panel, siempre que fuera gratis. Quick Tunnel está activo; se verificaron HTTPS, catálogo real y denegación 401 de la API administrativa sin sesión, además de login, panel, avisos, tienda y móvil en Edge por la dirección pública. No se creó ningún recurso Render ni de pago. La URL temporal actual está en `.tmp/url-publica.txt`; no es un dominio permanente.

```powershell
.\iniciar-demo.cmd -Publico -NoBuild
```

Arranca Cloudflare Quick Tunnel y obtiene una URL HTTPS temporal. Lee únicamente los logs del arranque actual para no reutilizar una dirección histórica tras reiniciar; actualiza `PUBLIC_BASE_URL` y `.tmp/url-publica.txt` para enlaces nuevos. No necesita cuenta ni dominio de Cloudflare y no crea recursos Render. PC/Docker deben seguir encendidos y conectados, sin suspensión. No tiene SLA; cambia de hostname al reiniciarse. Regenerar enlaces pendientes después de cambiar URL; los mensajes antiguos conservan su enlace. Los vencimientos usan hora real del servidor.

```powershell
docker compose --env-file .env.pruebas -p foodsave_pruebas -f compose.yaml -f compose.pruebas.yaml --profile publico stop
```

Detiene conservando datos. No usar `down -v` para detener. PostgreSQL/Redis no publican puertos. Uvicorn omite access logs para evitar tokens en rutas; proveedor usa no-store/no-referrer. [Referencia de Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

## Variables para tus amigos

| Variable | Uso / tratamiento |
|---|---|
| `POSTGRES_PASSWORD` | Privada, nueva por instalación Docker. |
| `JWT_SECRET` | Privada y estable: firma y cifrado Telegram. Rotarla requiere plan para el token cifrado. |
| `PUBLIC_BASE_URL` | Origen web público, no secreto. Cambia con el túnel. |
| `GOOGLE_CLIENT_ID` | OAuth público; registrar cada origen autorizado en Google Cloud. |
| `HABILITAR_CLIENTE_LOCAL` | `1` para las cuentas locales de prueba. |
| `HABILITAR_ENLACES_PROVEEDOR` | `1` incluye enlace en mensajes nuevos. |
| `NEXT_PUBLIC_TIENDA_MODO` | `api` por defecto; `ejemplo` solo maqueta explícita. Requiere rebuild. |
| `API_INTERNAL_URL` | Next → API: `http://api:8000` Docker; `http://127.0.0.1:8000` desarrollo/variante compacta. |
| `HABILITAR_DATOS_PRUEBA` | `1` solo carga explícita en base aislada. |
| `DEMO_ADMIN_PASSWORD`, `DEMO_OPERADOR_PASSWORD`, `DEMO_CLIENTE_PASSWORD` | Cuentas mock públicas del JSON al crear la demo; cambiar env no cambia hashes ya existentes. |
| `TELEGRAM_BOT_TOKEN` | Fallback privado; preferir Proveedores → configuración cifrada. Git no lo traslada. |

Compartir `.env.example` y esta guía; nunca publicar `.env`/`.env.pruebas`. El lanzador genera las claves necesarias. Google real requiere credencial OAuth del equipo, no se inventa. El bot puede reutilizarse configurando el token/chat privadamente.

## Render opcional, de pago

`render.yaml`/`Dockerfile.render`: web/API/worker/Beat dentro de una instancia con disco `/data`, PostgreSQL y Key Value privados. Modelos y credencial cifrada comparten disco dentro de la instancia, sin asumir discos compartidos entre servicios Render. Una sola instancia y Beat; no es escalado horizontal. Supervisor aplica migraciones, adapta URL psycopg, baja privilegios y detiene los demás procesos si uno termina. Disco conserva modelos/cifrado; reinicios implican interrupción.

**No aplicar con presupuesto cero.** Consultar costes actuales y confirmar workspace antes de crear. Render necesita código publicado en la rama autorizada; escribir el Blueprint no publica ni despliega. Los recursos de la cuenta existente se conservan.

## Instalación habitual y pruebas

Aplicar migración aditiva **0020_operacion_integrada** y actualizar API/worker/Beat/frontend juntos, con respaldo privado. Compose ejecuta migraciones antes de servicios. No se reescribe 0019 ni se ejecuta semilla en datos habituales. Downgrade se niega con historia operativa nueva.

Pruebas: `backend/tests/integration/test_operacion_integrada.py`. SQLite cubre reglas/transacciones; PostgreSQL acredita locks reales. La bitácora distingue lo comprobado en navegador, Docker, túnel o Render: la presencia de configuración no acredita un despliegue.
