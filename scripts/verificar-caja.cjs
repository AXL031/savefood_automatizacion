/* Codex para Axel / E01-E04. Requiere npm ci en frontend.
 * node scripts/verificar-caja.cjs
 * React/jsdom + API falsa en memoria: no red, no datos del comercio. Exit 1 si falla.
 */
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const Module = require('node:module');
const raiz = path.resolve(__dirname, '..');
const req = Module.createRequire(path.join(raiz, 'frontend/package.json'));
const { JSDOM } = req('jsdom');
const dom = new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>', { url: 'http://caja.test/' });
Object.assign(global, { window: dom.window, document: dom.window.document, HTMLElement: dom.window.HTMLElement,
  sessionStorage: dom.window.sessionStorage, IS_REACT_ACT_ENVIRONMENT: true });
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
dom.window.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
dom.window.HTMLDialogElement.prototype.close = function () { this.open = false; };
const ts = req('typescript');
for (const ext of ['.ts','.tsx']) require.extensions[ext] = (mod, file) => mod._compile(ts.transpileModule(fs.readFileSync(file,'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, esModuleInterop:true }, fileName:file }).outputText, file);
const resolver = Module._resolveFilename;
Module._resolveFilename = function (nombre, ...args) { return resolver.call(this, nombre.startsWith('@/') ? path.join(raiz,'frontend/src',nombre.slice(2)) : nombre, ...args); };
const React = req('react'), { act } = React, { createRoot } = req('react-dom/client');
const { CajaPresencial, importeCaja } = require('../frontend/src/features/ventas/CajaPresencial.tsx');
let venta = null, posts = [], perderRespuesta = false;
const producto = { id:1,codigo:'PAN',nombre:'Pan de prueba',activo:true,precio:'2.50',version_precio:1,stock_conocido:true,disponible:5,aviso_caducidad:false };
const cot = { id:'11111111-1111-4111-8111-111111111111',moneda:'PEN',total:'2.50',vence_en:'2026-10-26T15:05:00Z',lineas:[{ producto_id:1,cantidad:1,nombre:'Pan de prueba',codigo:'PAN',precio:'2.50',subtotal:'2.50',precio_id:1,version_precio:1 }] };
const contexto = { token:'fixture',perfil:{id:1,rol:'OPERADOR',nombre:'Fixture'},negocio:{nombre:'Prueba aislada',zona_horaria:'America/Lima'} };
function ticket(body) { return { id:1,numero:'V-00000001',canal:'PRESENCIAL',estado:'CONFIRMADA',total:'2.50',moneda:'PEN',fecha_local:'2026-10-26',vendida_en:'2026-10-26T15:00:00Z',zona_horaria:'America/Lima',nombre_usuario:'Fixture',cobro:{...body.cobro_presencial,vuelto:'0.00'},anulacion:null,lineas:[{...cot.lineas[0],id:1,salidas:[{lote_id:1,cantidad:1,movimiento_id:1,compensacion_id:null}]}] }; }
global.fetch = async (url, opt={}) => {
  const ruta = new URL(url).pathname.replace('/api/v1',''), metodo = opt.method ?? 'GET';
  let datos, status=200, metadatos;
  if (ruta==='/ventas/catalogo') datos={fecha_local:'2026-10-26',zona_horaria:'America/Lima',moneda:'PEN',productos:[producto]};
  else if (ruta.startsWith('/ventas/tickets/por-clave/')) { datos=venta;status=venta ? 200 : 404; }
  else if (ruta==='/ventas/tickets' && metodo==='GET') { datos=venta ? [venta] : [];metadatos={total:datos.length,importe_confirmado:venta?'2.50':'0.00'}; }
  else if (ruta==='/ventas/cotizaciones') { datos=cot;status=201; }
  else if (ruta==='/ventas/tickets' && metodo==='POST') {
    const body=JSON.parse(opt.body); posts.push(body); venta ??= ticket(body); datos=venta;status=201;
    if (perderRespuesta) { perderRespuesta=false;throw new TypeError('Respuesta perdida controlada'); }
  } else throw new Error(`Solicitud inesperada ${metodo} ${ruta}`);
  return {ok:status<400,status,text:async()=>JSON.stringify(status===404?{error:{codigo:'VENTA_NO_ENCONTRADA',mensaje:'Aún sin resultado'}}:{datos,metadatos})};
};
const pausa = () => new Promise(r=>setTimeout(r,0));
async function ejecutar(accion) { await act(async()=> { accion?.(); await pausa(); await pausa(); }); }
function boton(texto) { const b=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===texto);assert.ok(b,`Falta botón: ${texto}`);return b; }
async function click(texto) { await ejecutar(()=>boton(texto).click()); }
async function prepararVenta() {
  await click('Registrar venta');
  const select=document.querySelector('dialog select');
  await ejecutar(()=>{select.value='1';select.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});
  await click('Agregar');await click('Cotizar y revisar');
  assert.ok(document.body.textContent.includes('Revisa tu venta'));
}
(async()=>{
  assert.equal(importeCaja('12,3'),'12.30');assert.equal(importeCaja('5'),'5.00');
  for (const x of ['1.234','NaN','-1','']) assert.throws(()=>importeCaja(x));
  let root=createRoot(document.getElementById('root'));
  await ejecutar(()=>root.render(React.createElement(CajaPresencial,{contexto})));
  assert.ok(!document.body.textContent.includes('Configurar precio'),'Operador no debe editar precios');
  await prepararVenta();
  const select=document.querySelector('dialog select');
  await ejecutar(()=>{select.value='YAPE';select.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});
  await ejecutar(()=>{select.value='EFECTIVO';select.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});
  await ejecutar(()=>{boton('Confirmar venta').click();boton('Confirmar venta').click();});
  assert.equal(posts.length,1,'Doble clic debe conservar una solicitud');
  assert.ok(document.body.textContent.includes('Stock actualizado'));
  assert.equal(sessionStorage.getItem('foodsave:caja:pendiente:1'),null);
  await ejecutar(()=>root.unmount());
  producto.disponible=0;
  root=createRoot(document.getElementById('root'));
  await ejecutar(()=>root.render(React.createElement(CajaPresencial,{contexto})));
  await click('Registrar venta');
  assert.equal(document.querySelector('dialog').open,true,'Abrir sin elegibles debe mostrar el diálogo');
  assert.ok(document.querySelector('dialog').textContent.includes('No hay productos disponibles para vender'));
  assert.ok(document.querySelector('dialog').textContent.includes('Todos tienen precio en soles'));
  assert.ok(document.querySelector('dialog').textContent.includes('1 sin stock vendible para hoy'));
  assert.equal(boton('Cotizar y revisar').disabled,true,'Sin stock no se puede cotizar');
  assert.equal(boton('Agregar').disabled,true);
  await click('Revisar catálogo y precios');
  assert.equal(document.querySelector('dialog'),null);
  assert.equal(document.querySelector('details').open,true,'La acción debe abrir el catálogo');
  await ejecutar(()=>root.unmount());
  producto.disponible=5;producto.precio=null;
  root=createRoot(document.getElementById('root'));
  await ejecutar(()=>root.render(React.createElement(CajaPresencial,{contexto})));
  await click('Registrar venta');
  assert.ok(document.querySelector('dialog').textContent.includes('1 sin precio de caja'));
  assert.equal(boton('Agregar').disabled,true,'Un precio ausente no se sustituye por cero');
  await ejecutar(()=>root.unmount());
  producto.disponible=5;producto.precio='2.50';
  venta=null;posts=[];perderRespuesta=true;
  root=createRoot(document.getElementById('root'));
  await ejecutar(()=>root.render(React.createElement(CajaPresencial,{contexto})));
  await prepararVenta();await click('Confirmar venta');
  assert.equal(posts.length,1);
  const guardada=JSON.parse(sessionStorage.getItem('foodsave:caja:pendiente:1'));
  assert.equal(guardada.clave_idempotencia,posts[0].clave_idempotencia);
  assert.ok(document.body.textContent.includes('Recuperar o confirmar la misma venta'));
  await ejecutar(()=>root.unmount());
  root=createRoot(document.getElementById('root'));
  await ejecutar(()=>root.render(React.createElement(CajaPresencial,{contexto})));
  assert.ok(document.body.textContent.includes('recuperada'));
  assert.equal(posts.length,1,'Restaurar respuesta no debe emitir otro POST');
  assert.equal(sessionStorage.getItem('foodsave:caja:pendiente:1'),null);
  await ejecutar(()=>root.unmount());
  console.log('OK: caja React: medio intercambiable, doble clic, confirmación, permisos y recuperación tras respuesta perdida/remontaje. API falsa, sin red.');
})().catch(e=>{console.error(e);process.exitCode=1;});
