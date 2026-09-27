# Guía de desarrollo — Autenticación y sesión

**Carpeta:** `backend/app/modules/autenticacion`.

**Responsable:** Axel Cueva. Responsable de interfaz, API, datos, reglas y pruebas de este dominio.

**Bloque:** Acceso, configuración y motor de automatizaciones. **Tareas:** A01.

## Leer antes de trabajar

- [Instrucciones para IA](../../../../AGENTS.md).
- [Reparto vigente y criterios de entrega](../../../../docs/equipo/responsabilidades.md).
- [Dependencias entre integrantes](../../../../docs/equipo/dependencias.md).
- [Alcance de la demo](../../../../docs/guia-inicio-desarrollo.md).
- [docs/api/contratos.md](../../../../docs/api/contratos.md).

## Punto de partida

Archivos técnicos observados al preparar esta guía: `__init__.py`, `modelos.py`, `rutas.py`. Su presencia no certifica que el recorrido esté completo. Consultar el resumen vigente de [Axel Cueva](../../../../docs/equipo/avances/cueva.md) para el último estado.

## Trabajo en esta carpeta

1. Completar validación de credenciales y perfil usando el núcleo existente.
2. Aplicar identidad pública y permisos Administrador/Operador a las rutas de dominio.
3. Uniformar errores 401/403 y tratamiento de sesión vencida.

## Organización de implementación

Crear archivos al necesitarlos: `esquemas.py` para entrada/salida y validación, `servicio.py` para casos de uso, `repositorio.py` para persistencia, `modelos.py` para tablas y `rutas.py` para HTTP. Las tareas asíncronas llaman al servicio público. Publicar contratos antes de que otro módulo los consuma.

**Entidades propias:** `usuario`. Cada migración se coordina con el esquema común; no escribir directamente tablas privadas de otro módulo.

## Dependencias y contrato de entrega

- **Recibe:** Credenciales o Bearer del cliente.
- **Entrega:** Perfil e identidad autorizada para todos los módulos.
- **Puede avanzar ahora:** reglas/formularios y pruebas con ejemplos de contrato identificados como fixtures.
- **Integración real:** requiere el servicio del proveedor descrito en [la matriz de dependencias](../../../../docs/equipo/dependencias.md). Documentar firma, campos, errores y ejemplo antes de conectar al consumidor.

## Criterios de terminado

- Credencial inválida o usuario inactivo no accede.
- Operador no puede ejecutar una operación administrativa.
- API, tipos, persistencia e interfaz propios coinciden; pruebas relevantes documentadas con resultados reales.

## Documentar el avance y entregar al siguiente

Al finalizar un avance significativo, actualizar [el registro del responsable](../../../../docs/equipo/avances/cueva.md) siguiendo [la plantilla](../../../../docs/equipo/avances/README.md): resumen vigente, tarea, comportamiento disponible, contrato/ejemplo, archivos clave, pruebas, bloqueos y próximo consumidor. En carpetas compartidas, el autor del dominio registra en su propio archivo y enlaza la coordinación. Actualizar esta guía y el contrato si cambian. No dejar el único resumen en el chat.
