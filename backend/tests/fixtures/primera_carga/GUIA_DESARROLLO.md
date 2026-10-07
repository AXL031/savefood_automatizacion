# Guía de desarrollo — Primera carga sintética

**Responsable:** Edu Sanchez; integración transversal E03/K01 coordinada por Axel.

Leer [guía padre](../GUIA_DESARROLLO.md), [contrato de importación](../../../../docs/api/contrato-importaciones.md) y [política ML](../../../../foodsave-ml/POLITICA_EVALUACION.md).

Los cinco CSV son un escenario **sintético** de tres productos y dos ingredientes. Ventas de enero a septiembre de 2022: entrenamiento enero–julio, validación agosto y prueba septiembre. Una venta ausente sigue siendo desconocida; los ceros explícitos se conservan. Recetas y cantidades son ejemplos de software, no fórmulas comerciales.

En `/inicializacion`, adjuntar `ventas.csv`, `productos.csv`, `ingredientes.csv`, `recetas.csv` y `stock_inicial.csv`. Fecha objetivo `2022-09-24`, referencia de stock `2022-09-23`, clave de importación `demo-completa-1`. Validar y aceptar en una instalación vacía. No reinicializar una base existente para usar el ejemplo; las pruebas crean su propio esquema.

Comprobar carga, preparación automática y evaluación histórica desde API/worker/Beat reales. No hay proveedores, credenciales ni envío externo. El test `test_preparacion_e03.py` consume estos archivos y verifica recuperación sin reimportar. Actualizar esta guía y el avance de coordinación si cambian el escenario o su contrato.

Tras MODELO_LISTO, en Automatizaciones seleccionar los IDs de los tres productos, fecha histórica `2022-09-24`, hora local `10:00` y una hora real futura. Beat genera el plan y solicita evaluación. Abrir el plan desde el detalle de ejecución o Planificación. Cada producto resta stock elegible; harina/levadura se agregan en g según receta. Para volver a calcular desde una corrida existente, crear un nuevo plan; la versión anterior permanece. Stock desconocido aparece como aviso y bloquea compras. Este ejemplo no incluye proveedores ni destinos: la propuesta de compra queda BLOQUEADA y no transmite mensajes.
