# Flujo de trabajo con Git

## Ramas del equipo

Cada integrante trabaja en una rama permanente con su apellido en minúsculas. Las ramas parten de `main` y cada persona desarrolla todos sus módulos dentro de su propia rama.

```text
main
├── cueva       # Axel Cueva
├── sanchez     # Edu Sanchez
├── bohorquez   # Kevin Bohorquez
├── vera        # Leonardo Vera
├── aguirre     # Leonardo Aguirre
└── rojas       # Max Rojas
```

`main` conserva la versión estable. Las ramas personales se integran mediante una solicitud de incorporación después de revisar pruebas, contratos y conflictos. No se crean ramas adicionales por funcionalidad, corrección o documentación para el trabajo normal del equipo; el cambio se realiza en la rama del integrante responsable.

## Comandos iniciales

Desde la raíz del repositorio:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c cueva
git push -u origin cueva
```

Repite las dos últimas líneas sustituyendo `cueva` por `sanchez`, `bohorquez`, `vera`, `aguirre` o `rojas` para crear cada rama. Si la rama ya existe en el remoto, usa `git switch cueva` y luego `git pull --ff-only origin cueva`.

Para el trabajo diario, cada integrante comprueba su rama y sube sus cambios así:

```bash
git switch cueva
git pull --ff-only origin cueva
git status
git add ruta/de/sus/cambios
git commit -m "funcion(modulo): describir cambio"
git push
```

Antes de abrir una solicitud hacia `main`, la persona actualiza su rama desde `main` y resuelve los conflictos localmente:

```bash
git switch cueva
git fetch origin
git merge origin/main
git push
```

La solicitud debe indicar módulos afectados, forma de probarlos, migraciones, dependencias y capturas si aplica. La integración se hace solo después de que otra persona revise el cambio. Las migraciones de Alembic ya aplicadas no se reescriben; si hay dos ramas con migraciones nuevas, se integran y se corrige el orden antes de ejecutar `upgrade head`.

Convención de mensajes de cambios:

```text
funcion(inventario): agregar movimiento de existencias
correccion(compras): evitar pedidos duplicados
prueba(automatizacion): verificar politica de reintentos
```

Cada solicitud debe incluir descripción, módulo afectado, forma de probarlo, dependencias y capturas si aplica. Antes de incorporarla, deben pasar las pruebas y el análisis estático, recibir aprobación de revisión y no tener conflictos.
