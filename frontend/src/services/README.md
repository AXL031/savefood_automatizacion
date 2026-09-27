# Servicios

`http.ts` es el único lugar que construye solicitudes a `/api/v1`, interpreta el sobre `{ datos }` y convierte errores de API o conexión en `HttpError`. Los archivos de dominio (`autenticacion.ts`, `automatizaciones.ts`, `notificaciones.ts`) exponen funciones tipadas para las pantallas. Añade servicios nuevos por dominio; evita `fetch` directo en componentes.

`sesion.ts` administra el token en `sessionStorage`. El servidor sigue siendo la fuente de verdad: una sesión guardada en el navegador no concede acceso si el token expiró.
