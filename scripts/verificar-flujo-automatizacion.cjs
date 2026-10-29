/* Axel Cueva / A03. Requiere npm ci en frontend. No consulta APIs ni modifica datos.
 * node scripts/verificar-flujo-automatizacion.cjs [--preview]
 * --preview genera HTML de fixtures en .tmp/automatizacion-preview. Exit 1 ante fallo.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const raiz = path.resolve(__dirname, '..');
const req = createRequire(path.join(raiz, 'frontend/package.json'));
const ts = req('typescript');
const React = req('react');
const { renderToStaticMarkup } = req('react-dom/server');
for (const extension of ['.ts', '.tsx']) require.extensions[extension] = (modulo, archivo) => {
  const { outputText } = ts.transpileModule(fs.readFileSync(archivo, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true },
    fileName: archivo,
  });
  modulo._compile(outputText, archivo);
};
const { describirFlujo, tieneId } = require('../frontend/src/components/automatizacion/estadoFlujo.ts');
const { FlujoEjecucion } = require('../frontend/src/components/automatizacion/FlujoEjecucion.tsx');
const inicio = '2026-10-21T15:00:00Z';
const base = {
  id: 100, programacion_id: 20, tipo: 'GENERAR_PROPUESTA', clave_idempotencia: 'fixture', huella_entrada: 'fixture',
  datos_entrada: { ejecutar_desde_utc: inicio, parametros: { fecha_objetivo_demo: '2026-09-29', producto_ids: [1, 2, 3] } },
  estado: 'PENDIENTE', inicio_en: null, fin_en: null, proximo_intento_en: null,
  despachada_en: null, lease_hasta: null, datos_salida: null, mensaje_error: null, intentos: [],
};
const fixtures = {
  pendiente: base,
  cola: { ...base, despachada_en: inicio },
  activa: { ...base, estado: 'EN_EJECUCION', despachada_en: inicio, inicio_en: inicio,
    intentos: [{ id: 1, numero_intento: 1, inicio_en: inicio, fin_en: null, estado: 'EN_EJECUCION', mensaje_error: null }] },
  reintento: { ...base, estado: 'REINTENTANDO', inicio_en: inicio, proximo_intento_en: '2026-10-21T15:01:00Z', mensaje_error: 'Fallo transitorio de infraestructura interna.' },
  completada: { ...base, estado: 'COMPLETADA', inicio_en: inicio, fin_en: '2026-10-21T15:00:18Z', datos_salida: { corrida_id: 42, plan_id: 8, propuesta_compra_id: 5, pedidos_estado: 'GENERADOS', evaluacion_ejecucion_id: 101 } },
  recompra: { ...base, estado: 'COMPLETADA', datos_salida: { corrida_id: 43, plan_id: 9, pedidos_estado: 'RECOMPRA_FECHA' } },
  fallida: { ...base, estado: 'FALLIDA', mensaje_error: 'No disponible <script>alert(1)</script>' },
  cancelada: { ...base, estado: 'CANCELADA' },
};
const estados = e => describirFlujo(e).pasos.map(p => p.estado);
assert.deepEqual(estados(fixtures.pendiente), ['listo', 'actual', 'pendiente', 'pendiente']);
assert.deepEqual(estados(fixtures.cola), ['listo', 'listo', 'pendiente', 'pendiente']);
assert.equal(estados(fixtures.activa)[2], 'actual');
assert.equal(estados(fixtures.reintento)[2], 'actual');
assert.deepEqual(estados(fixtures.completada), ['listo', 'listo', 'listo', 'listo']);
assert.equal(estados(fixtures.fallida)[2], 'error');
assert.ok(!estados(fixtures.cancelada).includes('actual'));
assert.equal(describirFlujo({ ...base, programacion_id: null }).pasos[0].titulo, 'Registrada');
for (const valor of [0, -1, 1.5, '1', null, NaN, Infinity]) assert.equal(tieneId(valor), false);
const html = (e, extra = {}) => renderToStaticMarkup(React.createElement(FlujoEjecucion, { ejecucion: e, zona: 'America/Lima', ...extra }));
const completada = html(fixtures.completada);
for (const enlace of ['/pronosticos?corrida_id=42', '/planificacion?plan_id=8', '/compras?plan_id=8', '/automatizaciones/ejecuciones/101']) assert.ok(completada.includes(enlace));
assert.ok(!html(fixtures.recompra).includes('href="/compras'));
assert.ok(!html(fixtures.activa).includes('href="/compras'));
assert.ok(!html(fixtures.fallida).includes('<script>'));
assert.ok(html(fixtures.fallida).includes('&lt;script&gt;'));
assert.ok(!html(fixtures.cancelada).includes('aria-current="step"'));
assert.ok(html(fixtures.activa).includes('aria-current="step"'));
assert.ok(html(fixtures.activa, { desactualizado: true }).includes('Sin conexión'));
assert.ok(html(fixtures.activa, { compacto: true }).includes('/automatizaciones/ejecuciones/100'));
assert.ok(html({ ...fixtures.activa, datos_entrada: { parametros: { prueba_repetible: true } } }).includes('Prueba repetible'));
console.log('OK: 8 estados/escenarios; enlaces, errores escapados, accesibilidad y desconexión. Sin acceso a APIs.');
if (process.argv.includes('--preview')) {
  const destino = path.join(raiz, '.tmp/automatizacion-preview');
  fs.mkdirSync(destino, { recursive: true });
  fs.copyFileSync(path.join(raiz, 'frontend/src/app/styles.css'), path.join(destino, 'styles.css'));
  for (const [nombre, e] of Object.entries(fixtures)) {
    const documento = `<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="styles.css"><style>main{max-width:1200px;margin:40px auto;padding:0 20px}nav{display:flex;gap:16px;flex-wrap:wrap}h1{margin-top:28px}@media(max-width:600px){main{margin:24px auto;padding:0 12px}}</style><title>Fixture de automatización</title><main><nav>${Object.keys(fixtures).map(n => `<a href="${n}.html">${n}</a>`).join('')}</nav><p class="helper-text">Vista de prueba · datos ficticios · no ejecuta automatizaciones</p><h1>Ejecución #100</h1>${html(e, { actualizadoEn: '2026-10-21T15:00:18Z' })}</main></html>`;
    fs.writeFileSync(path.join(destino, nombre + '.html'), documento);
  }
  console.log('Preview: .tmp/automatizacion-preview/activa.html');
}
