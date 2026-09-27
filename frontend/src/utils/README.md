# Utilidades

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Edu Sanchez**. Tareas, dependencias y avances se detallan en la guía local.

Funciones puras que no dependen de React, del navegador ni de la API. `fechas.ts` da formato a instantes con la zona horaria del comercio y calcula duraciones; `numeros.ts` da formato a importes y cantidades con unidades; `estados.ts` traduce los estados de ejecución a etiquetas y tonos consistentes.

Las reglas de planificación, compras, excedentes y reintentos pertenecen a sus módulos o al backend, no a `utils/`.
