# Lighthouse de FoodSave — 04-11-2026

Estado: **PARCIAL**. Auditoría de escritorio iniciada en la rama `vera`; falta iniciar sesión en la ventana de Chrome de auditoría para medir las pantallas protegidas. No se han aplicado correcciones de interfaz.

## Condiciones y resultados iniciales

Lighthouse 13.6.0, configuración Desktop, categorías Performance y Accessibility, tres ejecuciones por URL y mediana. Medición sobre el frontend de producción en Docker, puerto 3000. Herramientas instaladas fuera del proyecto; ninguna dependencia añadida a FoodSave. Los resultados no constituyen una certificación completa de accesibilidad.

| Pantalla realmente medida | Performance | Accessibility | FCP (ms) | LCP (ms) | CLS | TBT (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Login anterior, tras redirección desde `/` | 97 | 100 | 169,28 | 213,14 | 0,10444 | 0 |
| Login directo, compilación actual de vera | 100 | 100 | 204,27 | 204,27 | 0,00031 | 0 |

Estas filas corresponden a versiones y recorridos distintos: **no son un antes/después atribuible a una corrección**. El primer resultado detecta desplazamiento al redirigir; no debe interpretarse como rendimiento del panel.

## Preparación verificada

- La instalación inicial servía una compilación anterior al código de `vera` (metadatos, menú e Inicio distintos).
- `docker compose build frontend`: correcto, 25 rutas generadas; incluye comprobación de tipos de Next.
- `docker compose up -d --no-deps frontend`: frontend actualizado sin reconstruir ni reiniciar los demás servicios.
- `docker compose exec -T frontend npm run typecheck -- --incremental false`: correcto. El intento previo sin esa opción falló al escribir tsconfig.tsbuildinfo por permisos del usuario del contenedor, no por errores TypeScript.
- Sesión administrativa de la pestaña original identificada; el navegador dedicado no comparte su sessionStorage. Se solicitó al usuario iniciar sesión allí, sin enviar contraseñas al chat.
- Evidencia local privada: `.tmp/lighthouse/montada/` y `.tmp/lighthouse/login-antes/`, tres JSON resumidos por medición. No se publican tokens ni credenciales.

## Trabajo pendiente

Medir con sesión Inicio, Productos, Inventario, Promociones, Ingredientes, Recetas, Ventas, Tienda administrativa, Automatización, Planificación, Operaciones, Proveedores, Compras, Pronósticos, Evaluación histórica, Informes, Configuración, Usuarios, Notificaciones e Inicialización/piloto. Los detalles de ejecuciones y el portal de proveedor requieren registros/enlaces existentes; documentar su inaccesibilidad si no los hay. El redireccionamiento a la tienda independiente no forma parte de esta auditoría.

Después de establecer esa línea base, corregir únicamente hallazgos reproducibles, revisar consumidores y navegación por teclado, volver a compilar, repetir tres mediciones por ruta y publicar la comparación. No crear registros comerciales ni enviar mensajes para conseguir cobertura. Los commits de correcciones y comentarios útiles se realizarán cuando exista evidencia que los justifique; no se inventa una cantidad de cambios.
