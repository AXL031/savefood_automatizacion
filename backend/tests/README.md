# Pruebas

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Axel Cueva**. Tareas, dependencias y avances se detallan en la guía local.

Pruebas generales del servidor; cada módulo puede añadir sus pruebas propias.

Las suites unitarias e integradas verifican contratos HTTP, permisos, atomicidad, idempotencia, versiones, compras/recuperación, ML y promociones. `test_evaluacion_revisiones.py` comprueba corrección→reserva→evaluación exacta, rollback, paginación de más de 50 corridas y subida acotada.

Desde la raíz, con Python 3.12+ y `backend[test,ml]` instalado:

```powershell
python -m pytest backend/tests/unit backend/tests/integration foodsave-ml/tests -q
```

Las pruebas PostgreSQL/Redis requieren servicios aislados y `A03_POSTGRES_TEST=1`, `V02_POSTGRES_TEST=1` y/o `E03_POSTGRES_TEST=1`; el CI ejecuta ese corte por separado. Una omisión no acredita concurrencia, DDL transaccional ni Beat real. Nunca usar datos o colas habituales para sustituir las fixtures aisladas. Telegram se prueba con transporte falso; un envío externo requiere autorización expresa.
