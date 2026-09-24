# Flujo de trabajo con Git

Ramas propuestas:

```text
main
desarrollo
funcionalidad/*
correccion/*
refactorizacion/*
documentacion/*
```

Cada persona trabaja en una rama de su módulo, abre una solicitud de incorporación y solicita revisión antes de unirla a `desarrollo`. Después de las pruebas de integración, los cambios pasan a `main`.

Convención de mensajes de cambios:

```text
funcion(inventario): agregar movimiento de existencias
correccion(compras): evitar pedidos duplicados
prueba(automatizacion): verificar politica de reintentos
```

Cada solicitud debe incluir descripción, módulo afectado, forma de probarlo, dependencias y capturas si aplica. Antes de incorporarla, deben pasar las pruebas y el análisis estático, recibir aprobación de revisión y no tener conflictos.
