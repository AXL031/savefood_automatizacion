# Flujos de integración continua

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

`base-ci.yml` construye el proyecto con Compose, aplica la migración inicial y comprueba API, interfaz y trabajador. Cuando los módulos tengan pruebas propias, se añadirán comprobaciones de servidor e interfaz. El resultado de CI depende de ejecutar el flujo en GitHub; una revisión estática local no lo sustituye.
