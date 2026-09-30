# Guía de desarrollo — Cliente HTTP y servicios por dominio

**Carpeta:** `frontend/src/services`.

**Responsable:** Edu Sanchez. Coordina esta carpeta compartida; los dueños de cada dominio implementan sus cambios.

**Bloque:** Inicialización, productos, ventas y estructura visual compartida.

## Leer antes de trabajar

- [Instrucciones para IA](../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../docs/api/contratos.md).
- [docs/api/rutas-api.md](../../../docs/api/rutas-api.md).

## Punto de partida

**30-09-2026 · Paso 5: compras.ts consume configuración Telegram (GET/POST/DELETE), comprobar bot, buscar chats y verificar destino usando cliente común. Credencial solo en body administrativo, sin URL ni almacenamiento del navegador.**

**Paso 2 local · 30-09-2026:** planificacion.ts usa el cliente HTTP común para listado/detalle/generación de planes M02. Mismo sobre, Bearer, abort y códigos de error.

**Paso 1 · 30-09-2026:** inicializacion.ts añade reintentarPreparacion sin archivos ni cuerpo; devuelve ConfiguracionInicial ampliada y mantiene cliente HTTP/autenticación comunes.

Archivos técnicos observados al preparar esta guía: `autenticacion.ts`, `automatizaciones.ts`, `http.ts`, `notificaciones.ts`, `sesion.ts`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Edu Sanchez](../../../docs/equipo/avances/sanchez.md) para el último estado.

## Trabajo en esta carpeta

**Frontera A01:** `http.ts` conserva el sobre `error.codigo/mensaje/detalles` del servidor y emite `foodsave:sesion-vencida` cuando una solicitud protegida devuelve 401. `ProtectedShell` elimina el token de sesión y redirige al acceso. Edu puede consumir este contrato sin crear otro manejo de Bearer para cada pantalla.

**Frontera A02:** `automatizaciones.ts` consume las cinco rutas reales de programación y ejecución; devuelve los `datos` tipados de A02 y no ofrece reintento manual.

1. Mantener http.ts como transporte; Axel acuerda autenticación y errores.
2. Cada dueño implementa archivo de servicio de sus rutas y trata tipos/estados definidos.
3. Edu agrega multipart para archivos sin imponer Content-Type JSON; mantener cancelación y errores por campo.
   `http.ts` acepta `formData` para la carga piloto y deja que el navegador genere el límite multipart. `inicializacion.ts` consume la ruta administrativa real.
4. No usar un 404 como datos vacíos ni simular persistencia para completar la demo.

## Límites y coordinación

Esta carpeta ofrece infraestructura o documentación a los módulos. Cada dueño entrega las reglas y pruebas de su bloque; un cambio de contrato compartido se documenta con el consumidor antes de integrarlo. Respetar responsables específicos de las subcarpetas.

## Criterio de entrega

El cliente conserva códigos/detalles útiles; una respuesta sin datos no parece válida.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../docs/equipo/avances/sanchez.md) siguiendo [la plantilla](../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Gestión de usuarios local · 30-09-2026

A01 ampliado por Codex para Axel: API /usuarios y pantalla administrativa para listado, creación, edición de datos/roles y activación. Contraseñas protegidas y respuestas sin hash; última cuenta administrativa activa protegida con locks ordenados. Sin migración. PostgreSQL: 13 pruebas de usuarios/acceso correctas, incluidas operaciones concurrentes. Typecheck y build correctos. Guía/mapa de /usuarios actualizados; sin publicación remota.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Contrato L03 · Paso 6

Compras incorpora aprobarPedido (clave_idempotencia,chat_id_revisado), rechazarPedido (clave,motivo) y verificarDestinosPropuesta. Pedido incluye decision, destino_actual, mensaje y envio (intento, chat conservado, tiempos/message_id/error saneado). UI conserva clave al repetir una solicitud; 202 es aprobación pendiente de worker, no envío confirmado. Destino actual es consulta viva, snapshots y mensaje aprobado permanecen. No exponer huella/token ni inventar estado ENVIADO. Contrato-pedidos y pruebas L03 son la referencia vigente.
