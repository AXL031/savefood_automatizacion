# Guía de desarrollo — Negocio y configuración

**Carpeta:** `frontend/src/app/configuracion`.

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

Archivos técnicos observados al preparar esta guía: `page.tsx`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

**Entrega A01:** el formulario ya guarda nombre, zona, moneda y modo de envío mediante la API real. Un Operador solo consulta. La selección automática afecta pedidos futuros y no envía nada por sí sola; Compras y Telegram siguen pendientes de Aguirre. Los errores del servidor son visibles y un 401 devuelve al inicio de sesión.

1. Construir formulario de negocio/zona/moneda con errores del servidor.
2. Mostrar selector de aprobación manual/automática y advertir que el cambio rige para pedidos nuevos.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

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

## Claridad y flujo completo · 30-09-2026

AUTOMATICO ya disponible para propuestas nuevas; preferencias futuras en sección explícita. Cambiar preferencia no altera pedidos conservados ni programaciones con modo explícito.
