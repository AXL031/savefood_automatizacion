# Registro de avances del equipo

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

**Coordinación:** Axel Cueva. **Autoría:** cada integrante mantiene su archivo. El registro inicial refleja el reparto documental; no certifica implementación de tareas nuevas.

| Integrante | Registro | Bloque |
|---|---|---|
| Axel Cueva | [cueva.md](cueva.md) | Acceso, configuración, automatización e infraestructura |
| Edu Sanchez | [sanchez.md](sanchez.md) | Inicialización, productos, ventas y UI común |
| Kevin Bohorquez | [bohorquez.md](bohorquez.md) | ML, evaluación y dashboard |
| Leonardo Vera | [vera.md](vera.md) | Inventario y promociones sugeridas |
| Leonardo Aguirre | [aguirre.md](aguirre.md) | Proveedores, pedidos y Telegram |
| Max Rojas | [rojas.md](rojas.md) | Ingredientes, recetas y planificación |

## Instrucción obligatoria para personas e IA

Al terminar un avance significativo de su bloque, y antes de entregar el trabajo o abrir una solicitud de incorporación, actualizar el registro del responsable. Si una tarea queda interrumpida, registrar el estado parcial y el siguiente paso. No es necesario registrar cada edición menor, pero ninguna entrega debe depender solo del historial del chat.

Mantener **Resumen vigente** al inicio para que el siguiente desarrollador sepa qué puede usar sin recorrer todos los archivos. Añadir una entrada a **Bitácora** (la más reciente primero), conservando las anteriores. Fechas en America/Lima. Si cambia una frontera, actualizar también su contrato y GUIA_DESARROLLO.md. Los avances se registran con nombre del autor real (persona o IA actuando para el bloque), sin atribuir pruebas no ejecutadas.

## Contenido mínimo de una entrada

```text
Fecha/hora y zona:
Autor y responsable del bloque:
Tareas (A01, E02, K02, V01, L03, M02...):
Estado: PENDIENTE | EN_CURSO | PARCIAL | BLOQUEADO | LISTO_PARA_INTEGRAR | INTEGRADO
Qué cambió y qué comportamiento está disponible:
Archivos clave (enlaces, solo los necesarios):
Contrato/función/ruta y ejemplo de uso:
Migración/configuración necesaria (sin valores secretos):
Pruebas: comando, resultado y límites del entorno:
Qué necesita el siguiente desarrollador y quién es:
Dependencias/bloqueos y responsable de resolverlos:
Siguiente paso concreto:
Commit/PR: enlace si existe; de lo contrario "cambios locales, sin commit".
```

Un check de tipos no equivale a una prueba de flujo. Un stub no es API disponible. «PARCIAL» indica qué parte existe y cuál falta. «LISTO_PARA_INTEGRAR» requiere contrato estable y ejemplo reproducible; «INTEGRADO» requiere evidencia de consumo por el siguiente bloque. Evitar listas exhaustivas de archivos, secretos, capturas con datos privados y afirmaciones vagas de avance porcentual.

## Lectura recomendada para continuar trabajo

1. Abrir [responsabilidades](../responsabilidades.md) y [dependencias](../dependencias.md).
2. Leer el resumen vigente propio y el del proveedor de la dependencia.
3. Abrir únicamente el contrato y archivos clave enlazados.
4. Verificar el ejemplo y actualizar el propio registro al entregar el cambio.
