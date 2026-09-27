# Interfaz

La aplicación Next.js incluye acceso, configuración del comercio, automatizaciones, detalle de ejecución y notificaciones. La configuración de nombre, zona horaria y moneda usa la API actual. Automatizaciones y notificaciones muestran estados honestos hasta que existan sus rutas de backend; ninguna acción se simula como guardada o enviada.

Rutas: `/iniciar-sesion`, `/configuracion`, `/automatizaciones`, `/automatizaciones/ejecuciones/[id]` y `/notificaciones`. La raíz redirige a configuración. El acceso protegido comprueba perfil y negocio antes de mostrar datos.

Los recursos comunes se dividen así: `src/services/http.ts` centraliza URL, cabeceras, respuesta `datos` y errores; cada servicio de dominio declara sus rutas. `src/types/` define contratos TypeScript; `src/utils/` contiene funciones puras de formato y estados; `src/components/ui/` contiene presentaciones reutilizables y `src/components/layout/` la navegación protegida. Evita duplicar `fetch`, etiquetas de estado y formato de fechas en cada módulo. Los dueños de cada dominio conservan sus reglas de negocio en su módulo.

El token de acceso se guarda solo durante la sesión de la pestaña mediante `sessionStorage`; una respuesta 401 lleva de vuelta a iniciar sesión. Esta es la solución del MVP con JWT actual. El cierre de sesión borra ese token local. Antes de una distribución comercial conviene evaluar cookies `HttpOnly` y un flujo de renovación de sesión.

Para verificar la interfaz: `npm install`, `npm run typecheck` y `npm run build` dentro de `frontend/`. El [README principal](../README.md) explica el arranque con Compose. Edu coordina los cambios globales de identidad visual y componentes compartidos; cada responsable puede usar estas piezas al construir su módulo.
