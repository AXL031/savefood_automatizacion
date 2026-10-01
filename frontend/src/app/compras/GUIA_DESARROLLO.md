# Guía de desarrollo — Pedidos, aprobación y envío

**Carpeta:** `frontend/src/app/compras`.

**Responsable:** Leonardo Aguirre. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Proveedores, pedidos y Telegram. **Tareas:** L02, L03, L04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).
- [docs/arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md](../../../../docs/arquitectura/decisiones/ADR-008-pedidos-desde-el-plan.md).

## Punto de partida

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Aguirre](../../../../docs/equipo/avances/aguirre.md) para el último estado.

## Trabajo en esta carpeta

1. Listar pedidos por plan/proveedor y detallar líneas, conversión y modo.
2. Mostrar aprobación solo a Administrador y solo en estado permitido.
3. Distinguir envío, fallo e incertidumbre; construir conciliación con evidencia según contrato.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

## Dependencias y contrato de entrega

- **Recibe:** Plan/necesidades de Max, ofertas propias y modo de negocio de Axel.
- **Entrega:** Pedidos trazables, estado de aprobación y resultado real del canal.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Repetir plan no duplica pedido; plan nuevo de misma fecha pasa control de recompra.
- Modo manual espera aprobación; automático usa datos/destino validados.
- Timeout después de transmitir queda PENDIENTE_VERIFICACION.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/aguirre.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.

## Paso 6 local · L03 · 30-09-2026

Aprobación/rechazo administrativos con clave idempotente, responsable, nombre y fecha; rechazo motivado de pendiente/bloqueado sin exigir canal. Aprobar exige modo manual, propuesta válida y chat revisado/verificado con credencial vigente. Congela texto/chat/huella y reserva envio_pedido en la misma transacción. Consultas/UI incluyen decisión, destino actual separado de snapshots, mensaje DEMOSTRACIÓN — NO SURTIR e intento/evidencia de Telegram. Aprobar no confirma envío; Beat/worker lo ejecutan y guardan message_id/fecha solo con respuesta válida.

Outbox con lease y token de despacho: revalida antes de transmitir y confirma ENVIANDO antes del efecto externo. Reentrega no vuelve a enviar; timeout, respuesta inválida o worker interrumpido quedan PENDIENTE_VERIFICACION sin retry. Cambiar destino/credencial bloquea antes de red. Ninguna acción mueve stock ni libera por sí sola la reserva de fecha. AUTOMATICO, conciliación y nuevos intentos humanos siguen en paso 7. Migración aditiva 0013; downgrade bloqueado si existen decisiones para no borrar evidencia. Contrato vigente: docs/api/contrato-pedidos.md; prueba test_aprobacion_envio_l03.py. Implementación local por Codex para Axel, responsabilidad de Aguirre, sin commit ni remoto; bot real pendiente del usuario.

## Claridad y flujo completo · 30-09-2026

Se muestran bloqueo y siguiente acción, destino actual, texto conservado y evidencia Telegram. Manual exige revisión explícita antes de aprobar. Automático válido no muestra aprobación; bloqueado corregido requiere nuevo plan. Estados/detalles diferencian cálculo completado de envío confirmado. Cantidades grandes en kg/L.


## Ajustes de interfaz · 30-09-2026

Tablas con paginador común y tamaños 10/25/50/100. Sesión/marco persistentes en AppShell; no usar recarga del documento para navegar. Detalle/edición en PanelDetalle, cierre/Escape y retorno a la página de origen; conservar permisos, snapshots y unidades. Las APIs mantienen listas recientes hasta 50 registros, identificadas en la pantalla; paginar esas filas no amplía el contrato histórico.

## Recuperación L04 · 01-10-2026

Codex para Axel bajo responsabilidad de Aguirre: POST /pedidos/{id}/conciliar registra ENVIADO o NO_ENVIADO con evidencia del último intento incierto; no transmite. POST /pedidos/{id}/reintentar reserva N+1 solo desde FALLIDO y con chat actual revisado/verificado. Conserva texto, plan, cantidades, autorización original e historial. GET incorpora envios/recuperaciones; envio sigue siendo el último. Locks fecha→propuesta→pedido→envío en recuperación/despacho/worker, respuesta tardía obsoleta ignorada. Clave/contenido/actor idempotentes, evidencia chat/message_id única. Usuario Operador consulta; solo Administrador actúa.

Migración aditiva 0014_l04_recuperacion sobre 0013, sin reescribir anteriores; downgrade bloqueado con acciones/reintentos. 57 pruebas PostgreSQL y 7 de migraciones correctas; typecheck/build correctos, API/UI/worker locales actualizados y alembic check sin diferencias. QA visual nuevo no acreditado: navegador integrado rechazó el entorno temporal con ERR_BLOCKED_BY_CLIENT. Pruebas usan transporte falso; no se envió otro Telegram. Contrato vigente: docs/api/contrato-pedidos.md, registro detallado en docs/equipo/avances/aguirre.md. Automático real, promociones y demo conjunta pendientes.
