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
