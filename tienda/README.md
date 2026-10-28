# Tienda independiente · Payme Flex de pruebas

Proyecto de la pastelería separado de FoodSave: frontend Next.js, API FastAPI y
volumen SQLite propios. Se puede copiar esta carpeta fuera del repositorio y
compilarla sin archivos, librerías Python, sesiones administrativas, modelos ni
base de datos de FoodSave. No requiere levantar FoodSave para probar Payme con el
catálogo de ejemplo.

## Entrar y configurar

Desde esta carpeta:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d --build
```

- Tienda: http://localhost:3101/tienda
- Checkout: http://localhost:3101/tienda/carrito (agregar primero un producto).
- API propia / OpenAPI: http://localhost:8001/docs
- FoodSave sigue en http://localhost:3100; sus enlaces `/tienda/*` redirigen al proyecto.

Completar **únicamente en `tienda/.env`** con los valores de preproducción de Payme:

```dotenv
PAYME_CLIENT_ID=
PAYME_CLIENT_SECRET=
PAYME_MERCHANT_CODE=
PAYME_HABILITADO=true
```

Después ejecutar `docker compose up -d --force-recreate api`. Los secretos nunca
son variables `NEXT_PUBLIC_*`. Sin los tres valores y la habilitación, la API
responde 503 al iniciar un pago y los cuatro botones aparecen deshabilitados.
No hay selector para producción: URLs auth/API/SDK están fijadas a sandbox.

Cada botón abre una instancia Flex con un único método: **Tarjetas → CARD**,
**Yape → YAPE**, **QR billeteras → QR**, **PagoEfectivo → PAGOEFECTIVO**.
Usar datos de prueba y métodos habilitados por Payme para ese comercio. La API
prepara el nonce; los datos de tarjeta se introducen exclusivamente en Flex.
El importe se calcula en el servidor y se verifica mediante Consulta o S2S.
El retorno del navegador nunca confirma por sí solo el pago.

## Notificaciones y pagos pendientes

Registrar con Payme una URL HTTPS pública que apunte a
`/api/v1/pagos/notificaciones` de la **API de la tienda**. Localhost no recibe
notificaciones externas. No se abre ningún túnel automáticamente. La firma RSA
se valida sobre los bytes originales con la llave pública de preproducción
publicada; `PAYME_WEBHOOK_PUBLIC_KEY` permite actualizarla si Payme la renueva.

Consulta desde el checkout o «Mis pedidos» permite verificar sin esperar el S2S
cuando ya se conoce la transacción. Si se abandona el navegador antes de recibir
un identificador, el S2S es necesario para recuperar ese resultado. Generar QR o
CIP no confirma pago. Cerrar Flex tampoco cancela una operación en el proveedor.
Un fallo de red conserva la clave y la operación para consultar o reabrir el
mismo intento. No iniciar una segunda compra mientras la anterior esté pendiente.

Puedes alternar los cuatro botones mientras solo hayas abierto un formulario y
no exista una transacción: se desmonta el anterior y se conserva la misma operación,
sin crear otra compra. Si ya hay una transacción/QR/CIP pendiente, el botón activo
permite consultar su estado; cambiar de vista no cancela el pago en Payme.

Las referencias privadas del navegador permiten consultar los pagos de prueba;
no constituyen cuenta Google verificada ni autorización para comprar con dinero
real. La base solo almacena hash de la capacidad UUID4, nunca PAN, CVV, Access
Token ni respuestas completas. El volumen `pagos` conserva estados al reiniciar.
No ejecutar `docker compose down -v` si se quieren conservar las pruebas.

## Comunicación con FoodSave

Solo HTTP a su API pública. `FOODSAVE_API_URL` configura la URL del navegador;
no hay imports de `backend/`, consultas SQL, montajes de sus archivos ni conexión
a su PostgreSQL. FoodSave debe permitir `TIENDA_ORIGIN` en CORS. Los cambios de
URLs públicas requieren reconstruir el frontend porque Next.js las incorpora
durante el build.

El modo actual es **`TIENDA_MODO=ejemplo`**: catálogo y disponibilidad son datos de
demostración; la cotización Payme usa el mismo catálogo versionado en la API
propia. Un pago aprobado de sandbox **no crea una venta, una entrega ni descuenta
inventario de FoodSave**. T01/T03/T04 de FoodSave siguen pendientes. No activar
`TIENDA_MODO=api` para cobrar hasta implementar cotización/reserva/confirmación
idempotente por API, autenticación de la integración y conciliación entre ambos
proyectos. No se deben reutilizar IDs ni precios de ejemplo como datos reales.
T02 de Google ya existe en el código de FoodSave, pero su despliegue/migración
0019 y configuración OAuth son independientes. El checkout Payme sandbox es de comprador
invitado y no muestra un paso de acceso con Google. El correo del comprador puede
ser de cualquier proveedor; Payme lo requiere como dato de facturación, sin sesión.

## Comprobar sin credenciales

```powershell
cd frontend
npm ci
npm run typecheck
npm run build
npm test
```

Pruebas backend: instalar `backend/requirements.txt` y `pytest`, ejecutar desde
`backend`: `python -m pytest tests -q`. Usan SQLite aislado y HTTP simulado; no
llaman a Payme ni a FoodSave. No equivalen a certificación con credenciales.
Las pruebas de interacción usan jsdom y un SDK Flex simulado para verificar cierre,
cambio de método, errores de nonce y respuestas tardías sin transmitir datos.

## Si Yape/QR queda cargando con `list index out of range`

El 21-10-2026 se reprodujo HTTP 500 en el servicio Flex del proveedor: su lista
sin filtro ofrecía CARD y PAGOEFECTIVO, sin YAPE/QR, con las credenciales locales.
Eso no demuestra qué está habilitado en el portal: requiere que Payme revise la
configuración de esos métodos para el merchant en **Flex sandbox**. No cambiar a
producción ni mostrar otro método en el botón como sustituto.
[Diagnóstico y texto para soporte](../docs/api/diagnostico-payme-sandbox-2026-10-21.md).

[Contrato Payme](../docs/api/contrato-payme-pruebas.md) ·
[Decisión de separación](../docs/arquitectura/decisiones/ADR-010-tienda-independiente-payme.md)

## Ampliación vigente · 28-10-2026 · Tienda por API

Para conectar el catálogo de FoodSave, desde la raíz ejecutar:

```powershell
node scripts/configurar-integracion-tienda.cjs
docker compose -f compose.yaml run --rm migraciones
docker compose -f compose.yaml up -d --build api frontend comercio
docker compose -f tienda/compose.yaml up -d --build api frontend conciliador
```

Usar los overrides de puertos locales de la instalación cuando corresponda (FoodSave de Axel: 3100). El script conserva Payme y genera/reutiliza dos secretos de integración distintos; estos son exclusivos de backend. Las URLs internas por defecto usan host.docker.internal:8000/8001, configurables en ambos .env. El modo api requiere FoodSave disponible para reservar/comprar. TIENDA_MODO=ejemplo permite probar Payme con el catálogo propio sin tocar stock de FoodSave.

En FoodSave: **Ventas → Publicar en tienda**, editar ficha/categoría/imagen opcional y publicar explícitamente. El precio procede de Ventas. Las promociones deben estar aprobadas y vigentes sobre lotes vendibles. El catálogo se entrega/reintenta cada diez segundos; stock visible se actualiza cada cinco segundos. No se publica automáticamente todo el catálogo ni se cargan existencias ficticias. Inventario → Registrar entrada permite dar de alta varios lotes con sus fechas.

En tienda: **Mis compras y pagos** no pide Google. Conserva enlaces privados de este navegador; otro navegador necesita su capacidad privada para consultar la compra. Pago aprobado y venta registrada son estados diferentes. Con fallo de red el conciliador reenvía el mismo evento; el botón Reintentar sincronización no cobra otra vez. Reserva predeterminada de veinte minutos (hasta la medianoche local); pagar después exige revisión, sin reembolso automático. Cierre de Flex no cancela el pago ni libera inmediatamente la reserva. La caja presencial respeta reservas y no permite anular pagos online.

Contrato y límites: [integración por API](../docs/api/contrato-integracion-tienda.md). Las pruebas ficticias no certifican que Payme haya habilitado Yape/QR para las credenciales del comercio.
