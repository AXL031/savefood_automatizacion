# Mockups de referencia

> Guía vigente: [GUIA_DESARROLLO.md](GUIA_DESARROLLO.md). Responsable de coordinación: **Edu Sanchez**.

Prototipos con datos ilustrativos de la propuesta de interfaz (semana 3). No son capturas de la app ni requisitos: ante cualquier diferencia mandan la [especificación visual](../especificacion-visual.md) y la [funcional](../../funcionalidades/especificacion-modulos.md). La numeración salta 02, 05 y 07 porque esas láminas no se entregaron.

| Archivo | Vista | Vigencia en la demo | Diferencias con el alcance |
|---|---|---|---|
| [01-guia-de-estilos.png](01-guia-de-estilos.png) | Sistema visual | Vigente | Ninguna (formato de números: ver spec visual) |
| [03-panel-principal.png](03-panel-principal.png) | Panel principal | Parcial | La demo usa **Panel histórico** (pronóstico vs. real); producción del día, excedentes y pérdida evitada son visión futura |
| [04-planificacion-de-produccion.png](04-planificacion-de-produccion.png) | Planificación | Base de M04 | Margen 0 % (no 3 %); sin columna «Confianza» (el modelo no la produce); sin «Aprobar plan» (se aprueban pedidos); fecha del escenario histórico, no «22:01»; agregar versión de receta y estados de cobertura |
| [06-compras.png](06-compras.png) | Compras | Base de L02–L04 | Estados de ADR-008 (`PENDIENTE_APROBACION`, envío Telegram); sin «Nuevo pedido» manual ni importes |
| [08-excedentes.png](08-excedentes.png) | Excedentes | Visión futura | No se construye |
| [09-promociones.png](09-promociones.png) | Promociones | Visión futura | En la demo solo hay **promociones sugeridas** (V03–V04) |
| [10-automatizaciones.png](10-automatizaciones.png) | Automatizaciones | Parcial | Programación a demanda despachada por Beat, no horarios fijos |
| [11-ejecucion-y-control.png](11-ejecucion-y-control.png) | Ejecución | Vigente | Intentos como `1 de 3`; «cambiar proveedor» y «pedido manual» son futuros |
| [12-configuracion.png](12-configuracion.png) | Configuración | Parcial | Límites, notificaciones e integraciones son futuros; la demo guarda datos del comercio y modo de envío |

Pantallas de la demo **sin mockup**: Iniciar sesión, Primera carga, Productos, Ventas, Ingredientes, Recetas, Inventario, Proveedores, Pronósticos y Panel histórico. Su diseño está en la tabla «Diseño por pantalla» de la [especificación visual](../especificacion-visual.md#diseño-por-pantalla).
