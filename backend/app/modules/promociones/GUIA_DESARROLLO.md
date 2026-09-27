# Guía de desarrollo — Promociones sugeridas

**Carpeta:** `backend/app/modules/promociones`.

**Responsable:** Leonardo Vera. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inventario por lotes y promociones sugeridas. **Tareas:** V03, V04.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/arquitectura/decisiones/ADR-007-automatizaciones-demo.md](../../../../docs/arquitectura/decisiones/ADR-007-automatizaciones-demo.md).
- [docs/automatizacion/flujos.md](../../../../docs/automatizacion/flujos.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `reglas.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Leonardo Vera](../../../../docs/equipo/avances/vera.md) para el último estado.

## Trabajo en esta carpeta

1. Reutilizar reglas.py y sus pruebas; persistir versión de regla y evaluación por lote.
2. Validar fecha límite, umbral, ventana horaria y frescura usando el reloj simulado.
3. Registrar proponer/descartar, descuento y motivo; enlazar con ejecución y ajuste.
4. Mostrar sugerencia sin activar precios ni usar CatBoost diario como modelo intradía.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `regla_promocion_demo`, `evaluacion_promocion`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Lectura pública de inventario, regla y hora local simulada.
- **Entrega:** Evaluación durable positiva o negativa para la pantalla de promociones.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Sin fecha o lectura vigente no se propone descuento.
- La evaluación no cambia saldo ni precios.
- Mensaje duplicado conserva una evaluación por ejecución/lote.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/vera.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
