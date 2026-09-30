# Dependencias y orden de entregas

La asignación vigente está en [responsabilidades](responsabilidades.md). Una dependencia bloquea la integración indicada, no todo el trabajo del integrante. Se puede avanzar con un fixture que respete el contrato, etiquetado como prueba, hasta que el proveedor entregue su servicio. No presentar una integración simulada como terminada.

## Entregas que otros necesitan

| Entrega | Responsable | Quién la necesita | Qué puede adelantar el consumidor | Qué bloquea su integración real |
|---|---|---|---|---|
| A01: identidad, permisos y error uniforme | Axel | Todos | Modelos, reglas puras y formularios con ejemplos de contrato | Rutas protegidas y manejo de errores consistente |
| A02: programación, ejecución durable, contratos y trazas | Axel | Edu, Kevin, Vera, Max y Aguirre | Ya pueden desarrollar y probar con sesión compartida, claves e IDs de fixture | Integrar su propio consumidor y demostrar la transacción de frontera |
| A03: Beat, lease y reintentos automáticos | Axel | Edu, Kevin, Vera, Max y Aguirre | Conectar servicios a las funciones públicas A02 y preparar tareas idempotentes | Carga→entrenamiento automático, plan programado y promoción tras ajuste |
| A04: imagen ML, volumen de artefactos, Compose y CI | Axel | Kevin, Aguirre y todo el equipo | Kevin desarrolla entrenamiento/inferencia contra `MODEL_ARTIFACT_DIR`; Aguirre implementa canal con token local opcional; todos prueban arranque | Declarar modelo o Telegram integrados requiere código y pruebas de sus dueños; reproducibilidad en otra PC requiere verificación de un compañero |
| E01: productos/SKU y lectura de ventas | Edu | Max, Vera y Kevin | Corte interno y migración `0002_e01_ventas`; CSV piloto cargado por HTTP en PostgreSQL local con 139 productos y 27 740 ventas; rutas y pantallas generales disponibles | Consumidores deben verificar sus fronteras con datos reales |
| M01: ingredientes, recetas y servicio de carga | Max | Edu, Vera y Aguirre | Parser/vista previa, movimientos con fixtures, proveedor/conversiones | Importación completa, lotes de insumo y oferta ligada a ingrediente |
| V01: apertura de lotes en sesión compartida | Vera | Edu | Validar hoja de stock sin persistirla | Confirmar carga atómica con apertura real |
| E02/E03: carga completa e identidad/estado inicial | Edu | Kevin y demo integrada | Asistente de dos XLSX o cinco CSV, vista previa, confirmación y estado durable implementados; piloto rápido CSV reserva `PREPARAR_MODELO` en la misma transacción | Conectar recetas de Max y apertura de Vera; vincular entrenamiento automático al asistente completo y verificar PostgreSQL |
| K02: corrida y pronóstico disponible | Kevin | Max | `generar_corrida` y `obtener_pronosticos` disponibles; corrida real probada con CSV piloto en SQLite | Max debe persistir plan enlazado a corrida; falta prueba integrada PostgreSQL |
| V02: disponibilidad de stock por fecha | Vera | Max | Cálculo con cantidades de ejemplo | Plan con stock elegible, lotes y advertencias reales |
| M03: necesidades agregadas por plan | Max | Aguirre | Oferta, conversión, estados, adaptador falso y pantalla de pedido | Crear pedido trazable desde el pronóstico real |
| L01: proveedor, oferta y chat verificado | Aguirre | Compras y demo | Probar cálculo y mensajes con cliente falso | Habilitar envío al chat de pruebas real |
| A01 + L02/L03: modo, aprobación y política de recompra | Axel configura; Aguirre aplica; Max entrega identidad del plan | Envío automático | Estados y pruebas de aprobación con entradas controladas | Enviar sin intervención con control de duplicados entre planes |
| K03: evaluación y API de métricas | Kevin | Su propia pantalla K04 | Backtest de 92 fechas y métricas persistidas probados localmente; API y panel K04 implementados | Falta comprobar API y worker sobre PostgreSQL/Compose y conectar evento de plan de Max |
| V02 + A03: ajuste/evento y despacho | Vera y Axel | Promociones de Vera | Probar la regla pura ya existente | Evaluación programada tras un ajuste real |
| E04: layout y componentes comunes | Edu | Todos | Pantallas propias usando las piezas actuales | Apariencia/navegación compartidas; no bloquea reglas de backend |

## Cómo evitar esperas innecesarias

1. **Primero contratos y fixtures:** el proveedor entrega firma, campos, tipos, errores y ejemplo antes de terminar la función. Consumidor valida el ejemplo y deja registrada la dependencia.
2. **No esperar el módulo completo:** Edu entrega productos e interfaz de ventas antes del asistente terminado; Max entrega servicio de recetas antes de la pantalla; Vera entrega apertura/lectura antes del historial visual; Kevin entrega corrida antes del dashboard.
3. **Resolver el ciclo de inicialización:** Edu orquesta una transacción; Max y Vera entregan funciones que reciben la misma sesión y no hacen commit. Cada uno puede probar su función con fixture sin esperar la carga completa. Al integrar, se prueba el rollback de toda la carga.
4. **Separar motor y tarea:** Axel entrega el envoltorio; Kevin/Max/Vera/Aguirre implementan sus funciones. Ninguno espera que Axel escriba la lógica de su dominio.
5. **Integrar en cortes pequeños:** contrato → servicio con prueba → ruta → pantalla → prueba con consumidor. No esperar al final para integrar seis ramas grandes.

## Ruta principal de la demo

Contratos y núcleo → catálogos/recetas/apertura → primera carga → entrenamiento e inferencia → plan con disponibilidad → pedidos → aprobación opcional y Telegram. El motor durable se desarrolla desde el inicio y debe estar disponible antes de integrar disparadores. La evaluación histórica/panel y el flujo de promociones se construyen en paralelo sobre esas entregas.

La regla entre planes de la misma fecha sigue siendo un contrato a cerrar por Aguirre y Max: la clave única por plan evita repetir ese plan, pero no evita por sí sola comprar nuevamente después de recalcular. Marcar esta dependencia como pendiente hasta documentar y probar la política; no habilitar envío automático suponiendo que ya está resuelta.

## Acuerdo de entrega entre dos responsables

El proveedor actualiza su [registro de avance](avances/README.md) y deja:

- ID de tarea y estado del servicio: disponible, parcial, simulado o pendiente.
- Enlace al contrato, versión/fecha y ejemplo mínimo de entrada/salida/error.
- Ruta HTTP o función pública, IDs/fixtures necesarios y migración requerida.
- Comando para probarlo y resultado observado; no solo «funciona».
- Consumidor esperado y limitaciones conocidas.

El consumidor lee ese resumen, prueba el ejemplo y registra en su propio avance si pudo integrar o qué error lo bloquea. La transferencia no se considera lista por existir una carpeta o un commit. Se conserva evidencia del comportamiento.
