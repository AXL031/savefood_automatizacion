# Dependencias y orden de entregas

**Paso 5 local · 30-09-2026:** L01/L03 entrega configuración administrativa Telegram, token cifrado, bot/chat y verificación ligada a credencial; UI y Compras consumen con 42 pruebas del corte (PostgreSQL/SQLite/transporte falso). Migración 0012 y volumen privado. El usuario aún no tiene bot: prueba real pendiente, sin mensajes. Aprobación/envío/conciliación siguen pasos 6/7. Detalle en [Aguirre](avances/aguirre.md) y coordinación [Axel](avances/cueva.md).

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
| E02/E03: carga completa e identidad/estado inicial | Edu | Kevin y demo integrada | Asistente de dos XLSX o cinco CSV, vista previa, confirmación y estado durable implementados; piloto rápido CSV reserva `PREPARAR_MODELO` en la misma transacción | M01/V01 conectados en main; paso 1 en cueva vincula ML/estados y verifica confirmación completa PostgreSQL. Revisar PR #11 y reproducir en otra PC |
| K02: corrida y pronóstico disponible | Kevin | Max | Paso 2 local consume generar_corrida, consultar_corrida y obtener_pronosticos; plan real probado con CatBoost/Beat/PostgreSQL | Revisión del corte local; publicación requiere permiso de Axel |
| V02: disponibilidad de stock por fecha | Vera | Max | Paso 2 local guarda stock elegible, lotes y advertencias; snapshots conservados tras ajustes | M03 local consume stock de ingredientes y guarda faltantes; publicación requiere permiso de Axel |
| M03: necesidades agregadas por plan | Max | Aguirre | obtener_necesidades disponible en local; API/motor real verificados, Decimal y snapshots | L02 debe exigir CALCULADAS y cerrar política entre planes de igual fecha; no integrado a compras |
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

## Paso 3 local · M03 · 30-09-2026

Necesidades y faltantes implementados en la transacción del plan. API/UI conservan aportes, unidades, lotes y lectura de stock; decimales como cadenas, agregación antes de redondear a tres decimales. Producción o stock ausente deja estado INCOMPLETAS y motivo; no se inventan ceros ni se modifica inventario. Migración aditiva 0010_m03_necesidades sobre 0009; planes antiguos quedan PENDIENTE_M03 y el administrador puede completarlos una vez. Servicio público obtener_necesidades y contrato M03 en docs/api/contratos.md. Compras y Telegram siguen pendientes. Cambios locales por Codex para Axel, sin commit ni cambios remotos.

## Paso 4 local · L01/L02 · 30-09-2026

Codex para Axel implementa compras bajo responsabilidad de Aguirre, consumiendo M03 de Max y modo de negocio de Axel por interfaces públicas. Migración aditiva 0011_l02_compras sobre 0010: propuesta_compra, pedido_compra y linea_pedido. Snapshots de necesidades, proveedor/oferta, factor, mínimo, múltiplo y modo; cálculo Decimal exacto. Una propuesta activa por fecha; cancelación administrativa motivada libera la fecha y conserva historial. Idempotencia por plan y bloqueo global ante datos/proveedor/destino incompletos. Sin faltantes no se crean pedidos ni se reserva fecha. No hay envíos ni cambios de stock.

API: POST /pedidos/generar {plan_id}, GET /pedidos y /pedidos/{id}, GET /compras/propuestas y /compras/propuestas/{id}, POST /compras/propuestas/{id}/cancelar {motivo}. UI /proveedores y /compras, enlace desde /planificacion; Operador consulta, Administrador modifica. GENERAR_PROPUESTA genera pedidos en su transacción y comunica RECOMPRA_FECHA sin perder el nuevo plan ni su evaluación. Servicios sin commit. Contrato actualizado en docs/api/contrato-pedidos.md; pruebas test_compras_l02.py y flujo real test_inicializacion_ml.py. Aprobación/envío siguen pendientes en L03 y nunca se declaran realizados por un borrador.
