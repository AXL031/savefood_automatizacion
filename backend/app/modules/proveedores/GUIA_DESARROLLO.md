# Guía de desarrollo — Proveedores y ofertas

**Carpeta:** `backend/app/modules/proveedores`.

**Responsable:** Leonardo Aguirre. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Proveedores, pedidos y Telegram. **Tareas:** L01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).

## Punto de partida

**30-09-2026 · Paso 5 (L01/L03): rutas administrativas de configuración/comprobación/búsqueda de chats; adaptador real y errores saneados. Verificación con fecha y huella de credencial; cambio de token/chat deshabilita su uso en UI y Compras. Migración 0012. Servicios sin commit; bloquear fila al vincular/verificar. Pruebas test_telegram_config_l03.py con transporte simulado. Validación real pendiente de bot propio; aprobación/envío son pasos 6/7.**

**Integración 30-09-2026:** L01 parcial integrado: Base y sesión comunes, autenticación/Administrador, sobre datos, FK de ingrediente y conversión restringida. Los servicios no hacen commit; HTTP coordina. Migración 0007. test_proveedores_l01.py forma parte de CI. Verificación Telegram devuelve false y explica adaptador ausente; no existe envío real ni UI nueva.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Aguirre](../../../../docs/equipo/avances/aguirre.md) para el último estado.

## Trabajo en esta carpeta

1. Implementar proveedor activo, código, nombre y vínculo del chat de pruebas.
2. Relacionar ingrediente con oferta, unidad de compra, factor, mínimo y múltiplo.
3. Garantizar una oferta preferida activa por ingrediente y publicar consulta para Compras.
4. Verificar destino mediante adaptador Telegram sin revelar credencial.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `proveedor`, `oferta_ingrediente`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Configuración administrativa y catálogo de ingredientes de Max.
- **Entrega:** Proveedor/oferta/destino válidos para generar y enviar pedidos.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- No se infieren conversiones por el nombre de la unidad.
- Destino no verificado bloquea envío.
- Oferta inválida o proveedor inactivo no habilita compra automática.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Consumidor L03 · Paso 6 local

`ServicioProveedores(sesion).consultar_destino(proveedor_id, bloquear=False)` devuelve la vista pública del destino efectivo para revisión de pedidos; con bloquear=True permite coordinar aprobación/envío con las escrituras de proveedor. No expone token ni huella. Compras separa esta consulta viva del snapshot inicial y exige chat_id_revisado al aprobar. Worker compara destino/credencial congelados antes de transmitir. Configuración/búsqueda/verificación del proveedor siguen sin mandar mensajes; solo la aprobación explícita en Compras reserva un envío. Modo automático pendiente del paso 7.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/aguirre.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.
