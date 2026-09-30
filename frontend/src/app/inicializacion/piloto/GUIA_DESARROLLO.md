# Guía de desarrollo — carga rápida del piloto

**Carpeta:** `frontend/src/app/inicializacion/piloto`. **Dominio:** inicialización y ventas de Edu Sanchez; coordinación de integración por Axel Cueva.

Leer las guías de `frontend`, `frontend/src`, `frontend/src/app` y `frontend/src/app/inicializacion`, [responsabilidades](../../../../../docs/equipo/responsabilidades.md), [dependencias](../../../../../docs/equipo/dependencias.md), [inicio](../../../../../docs/guia-inicio-desarrollo.md), [contrato de importaciones](../../../../../docs/api/contrato-importaciones.md) y [avance de Edu](../../../../../docs/equipo/avances/sanchez.md).

`page.tsx` recibe el CSV bakery original, llama a `cargarCsvPiloto`, presenta conteos y sigue la ejecución `PREPARAR_MODELO`. Puede reintentar el entrenamiento sin importar ventas otra vez. El asistente completo está en la ruta padre y requiere los contratos de Max y Vera para declarar la inicialización terminada.

El contrato HTTP es `POST /api/v1/inicializacion/piloto-bakery`, descrito en [contratos](../../../../../docs/api/contratos.md). Mantener permisos, manejo de error, sesión y estados de carga. Registrar cualquier cambio en el contrato, las pruebas y la bitácora del bloque, sin atribuir la edición a otro integrante.
