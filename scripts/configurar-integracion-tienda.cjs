// Configura exclusivamente la integración local HTTP; conserva credenciales Payme/DB/JWT.
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const raiz = path.resolve(__dirname, '..');
const rutas = [path.join(raiz, '.env'), path.join(raiz, 'tienda', '.env')];
for (const p of rutas) if (!fs.existsSync(p)) throw new Error('Crear primero el .env desde su ejemplo: ' + p);
const fuentes = rutas.map(p => fs.readFileSync(p, 'utf8'));
function valor(s, clave) { return s.split(/\r?\n/).find(l => l.startsWith(clave + '='))?.slice(clave.length + 1).trim() ?? ''; }
function token(claveRaiz, claveTienda) {
  const a = valor(fuentes[0], claveRaiz), b = valor(fuentes[1], claveTienda);
  if (a && b && a !== b) throw new Error('Los tokens configurados no coinciden para ' + claveRaiz + '; conciliar sin sobrescribirlos.');
  const t = a || b || crypto.randomBytes(32).toString('hex');
  if (t.length < 32) throw new Error('La credencial de integración debe tener al menos 32 caracteres.');
  return t;
}
const entrada = token('TIENDA_INTEGRACION_TOKEN', 'FOODSAVE_INTEGRACION_TOKEN');
const salida = token('TIENDA_PUBLICACION_TOKEN', 'FOODSAVE_PUBLICACION_TOKEN');
if (entrada === salida) throw new Error('Usar credenciales distintas por dirección.');
const cambios = [{ TIENDA_INTEGRACION_HABILITADA: '1', TIENDA_INTEGRACION_ID: 'tienda-local', TIENDA_INTEGRACION_TOKEN: entrada, TIENDA_PUBLICACION_TOKEN: salida, TIENDA_API_INTERNA_URL: 'http://host.docker.internal:8001', RESERVA_TIENDA_MINUTOS: '20' },
  { TIENDA_MODO: 'api', FOODSAVE_API_INTERNA_URL: 'http://host.docker.internal:8000', FOODSAVE_INTEGRACION_TOKEN: entrada, FOODSAVE_PUBLICACION_TOKEN: salida }];
const pendientes = fuentes.map((fuente, i) => {
  let lineas = fuente.split(/\r?\n/);
  for (const [clave, dato] of Object.entries(cambios[i])) {
    const indices = lineas.map((l, n) => l.startsWith(clave + '=') ? n : -1).filter(n => n >= 0);
    if (indices.length > 1) throw new Error('Variable duplicada: ' + clave);
    if (indices.length) lineas[indices[0]] = clave + '=' + dato;
    else lineas.push(clave + '=' + dato);
  }
  return lineas.join('\n').replace(/\n+$/, '') + '\n';
});
const respaldo = path.join(raiz, '.tmp', 'configuracion-integracion-tienda');
fs.mkdirSync(respaldo, { recursive: true });
for (let i = 0; i < rutas.length; i++) {
  const copia = path.join(respaldo, i ? 'tienda.env.antes' : 'foodsave.env.antes');
  if (!fs.existsSync(copia)) fs.writeFileSync(copia, fuentes[i], { mode: 0o600 });
}
for (let i = 0; i < rutas.length; i++) fs.writeFileSync(rutas[i], pendientes[i], { mode: 0o600 });
console.log('Integración HTTP local configurada. Se conservaron Payme, JWT, PostgreSQL y los valores ajenos. No se muestran tokens. Reconstruir y recrear servicios según tienda/README.md.');
