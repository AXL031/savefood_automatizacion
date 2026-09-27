# Guía de desarrollo — Negocio y configuración

**Carpeta:** `backend/app/modules/negocios`.

**Responsable:** Axel Cueva. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Acceso, configuración y motor de automatizaciones. **Tareas:** A01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contrato-pedidos.md](../../../../docs/api/contrato-pedidos.md).
- [docs/arquitectura/decisiones/ADR-005-instalacion-local-mvp.md](../../../../docs/arquitectura/decisiones/ADR-005-instalacion-local-mvp.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `__init__.py`, `modelos.py`, `rutas.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Mantener el único negocio local y validar zona IANA y moneda.
2. Persistir modo REQUIERE_APROBACION/AUTOMATICO y exponerlo a Compras.
3. Acordar los campos de identidad externa con Inicialización y evitar cambios que invaliden los datos importados.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `negocio`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Configuración administrativa del comercio.
- **Entrega:** Zona, identidad y modo de compra; Aguirre copia el modo al crear pedido.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Valores inválidos no se guardan.
- Cambiar el modo no modifica retroactivamente pedidos existentes.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
