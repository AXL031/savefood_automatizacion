# Flujos de integración continua

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

`base-ci.yml` se ejecuta en solicitudes de cambio y push de cualquier rama. Instala la suite Python con el extra `ml`, construye Compose, comprueba que Alembic llegó a todas las cabezas, verifica el volumen de artefactos compartido, el motor A03 con PostgreSQL/Redis, API, interfaz y trabajador. Cada dueño incorpora y corrige las pruebas de su módulo. El resultado de CI depende de ejecutar el flujo en GitHub; una revisión local no lo sustituye.
