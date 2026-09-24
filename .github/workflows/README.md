# Flujos de integración continua

`base-ci.yml` construye el proyecto con Compose, aplica la migración inicial y comprueba API, interfaz y trabajador. Cuando los módulos tengan pruebas propias, se añadirán comprobaciones de servidor e interfaz. El resultado de CI depende de ejecutar el flujo en GitHub; una revisión estática local no lo sustituye.
