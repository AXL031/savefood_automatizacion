# Configurar el inicio de sesión con Google de la tienda

Tienda del cliente, T02 ([ADR-009](../arquitectura/decisiones/ADR-009-tienda-cliente.md)). Sin esta configuración la tienda usa el login simulado.

## 1. Crear el ID de cliente en Google Cloud

1. Entrar a <https://console.cloud.google.com/> con la cuenta que administrará la tienda y crear o elegir un proyecto.
2. **APIs y servicios → Pantalla de consentimiento de OAuth** (Google Auth Platform → Branding/Público): tipo **Externo**, nombre «Pastelería Maria Juanita», correo de asistencia y del desarrollador. Mientras la app esté en modo **Prueba**, agregar en **Usuarios de prueba** cada Gmail que vaya a iniciar sesión.
3. **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**:
   - Tipo de aplicación: **Aplicación web**.
   - **Orígenes de JavaScript autorizados:** `http://localhost:3000` y `http://localhost`.
   - No hace falta URI de redireccionamiento (el botón de Google devuelve el token por ventana emergente).
4. Copiar el **ID de cliente** (`…apps.googleusercontent.com`). Es público; **no** se usa el secreto del cliente.

## 2. Configurar FoodSave

En el `.env` de la raíz (no se sube a Git):

```env
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
```

Opcional: `TIENDA_JWT_SECRET` con una cadena aleatoria larga. Si no se define, se deriva de `JWT_SECRET`.

Reconstruir y levantar (el ID se incorpora al frontend al compilar):

```powershell
docker compose build api migraciones worker frontend
docker compose up -d
```

La migración `0019_tienda_clientes` se aplica sola con el servicio `migraciones`.

## 3. Comprobar

Abrir `http://localhost:3000/tienda`, agregar un producto, ir a la canasta y pulsar **Iniciar sesión y confirmar**. Debe aparecer el botón oficial «Continuar con Google». Tras elegir la cuenta, el paso 1 muestra el nombre y el correo reales.

| Mensaje | Causa |
|---|---|
| `GOOGLE_NO_CONFIGURADO` | La API no recibió `GOOGLE_CLIENT_ID`: revisar `.env` y reconstruir `api`. |
| Error 400 `origin_mismatch` en la ventana de Google | Falta el origen exacto (`http://localhost:3000`) en la credencial. |
| «Acceso bloqueado: la app no completó la verificación» | La cuenta no está en **Usuarios de prueba**. |
| `GOOGLE_TOKEN_INVALIDO` | El ID de cliente del frontend y el de la API no coinciden, o el reloj del equipo está desfasado. |
| `GOOGLE_NO_DISPONIBLE` | El contenedor `api` no pudo descargar las claves públicas de Google (sin internet). |
