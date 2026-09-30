# Guía de desarrollo — Inventario por lotes y movimientos

**Carpeta:** `frontend/src/app/inventario`.

**Responsable:** Leonardo Vera. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Inventario por lotes y promociones sugeridas. **Tareas:** V01, V02.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).
- [docs/base_de_datos/esquema-objetivo-mvp.md](../../../../docs/base_de_datos/esquema-objetivo-mvp.md).

## Punto de partida

**Integración 30-09-2026:** Pantalla /inventario disponible desde rojas; muestra disponibilidad por fecha, lotes, movimientos y ajuste explícito. Typecheck y build verificados. Promociones V03 siguen pendientes.

La carpeta contiene documentación o estructura de destino; su existencia no declara API, página o servicio implementado. Consultar el resumen vigente de [Leonardo Vera](../../../../docs/equipo/avances/vera.md) para el último estado.

## Trabajo en esta carpeta

1. Listar lotes y totales con unidad, caducidad y vigencia desconocida.
2. Construir ajuste con motivo, delta y hora efectiva del escenario.
3. Mostrar movimientos y enlazar evaluación de promoción creada.

## Organización de implementación

La ruta compone `page.tsx` y componentes del feature correspondiente. Usar layout protegido y cliente HTTP común. Resolver carga, vacío, error, permisos y sesión vencida. Tener una carpeta y una guía no hace que la página exista: conectarla solo cuando su contrato esté publicado.

## Dependencias y contrato de entrega

- **Recibe:** Apertura o ajuste de lote y fecha objetivo para consultar.
- **Entrega:** Saldos, movimientos y disponibilidad; evento para evaluar promoción.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Repetición de clave no aplica delta dos veces; datos distintos producen conflicto.
- Concurrencia no deja stock negativo.
- Lote vencido no cuenta; vigencia desconocida se advierte.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/vera.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
