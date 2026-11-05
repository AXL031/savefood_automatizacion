/* Exploradores reales: 139 productos de plan/venta y listas de resumen, sin red. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const {JSDOM}=req('jsdom'),dom=new JSDOM('<!doctype html><div id="root"></div>',{url:'http://trazas.test/'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,IS_REACT_ACT_ENVIRONMENT:true});
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
dom.window.HTMLElement.prototype.scrollIntoView=function(){};
global.fetch=()=>{throw Error('Explorar trazas no debe consultar la red');};
const ts=req('typescript');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const resolver=Module._resolveFilename;
Module._resolveFilename=function(n,...a){return resolver.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...a);};
const React=req('react'),{act}=React,{createRoot}=req('react-dom/client'),h=React.createElement;
const {DetalleProductos}=require('../frontend/src/features/planificacion/DetalleProductos.tsx');
const {DetalleLineasVenta}=require('../frontend/src/features/ventas/DetalleLineasVenta.tsx');
const {ExploradorDetalle}=require('../frontend/src/components/tables/ExploradorDetalle.tsx');
const elementos=Array.from({length:139},(_,i)=>({producto_id:i+1,pronostico_id:800+i,cantidad_pronosticada:i===1?null:10,stock_disponible:i===1?null:2,cantidad_producir:i===1?null:8,estado:i===1?'STOCK_DESCONOCIDO':'CALCULADO',avisos:i===1?['VIGENCIA_STOCK_DESCONOCIDA']:[],
 stock:{codigo:`PRO-${i+1}`,nombre:i===0?'12 MACARON':i===1?'Azúcar especial':`Producto ${i+1}`,lotes:i===0?[{lote_id:1,codigo_lote:'VIGENTE',saldo:'2.000',cuenta:true,motivo:'VIGENTE',fecha_caducidad:'2026-11-06',fecha_limite_venta:'2026-11-05'},{lote_id:2,codigo_lote:'VENCIDO',saldo:'7.000',cuenta:false,motivo:'VENCIDO',fecha_caducidad:null,fecha_limite_venta:null}]:[]},
 receta:i===1?null:{receta_id:31+i,version:3,lineas:[{ingrediente_id:1,codigo:'ING-001',nombre:'Harina de trigo',cantidad_por_unidad:'250.000',unidad_base:'g'}]}}));
const lineas=elementos.map((e,i)=>({id:e.producto_id,producto_id:e.producto_id,nombre:e.stock.nombre,codigo:e.stock.codigo,cantidad:9,precio:'2.00',subtotal:'3.33',precio_id:10,salidas:Array.from({length:12},(_,n)=>({lote_id:n+1,cantidad:1,movimiento_id:n+100,compensacion_id:n===0?950:null}))}));
const original=JSON.stringify({elementos,lineas});
const pausa=()=>new Promise(r=>setTimeout(r,0));
async function ejecutar(fn){await act(async()=>{fn?.();await pausa();});}
function boton(texto,scope=document){const b=[...scope.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')===texto||b.textContent.trim()===texto);assert.ok(b,'Falta botón '+texto);return b;}
async function click(t,scope){await ejecutar(()=>boton(t,scope).click());}
async function buscar(v){const e=document.querySelector('input[type="search"]');await ejecutar(()=>{Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype,'value').set.call(e,v);e.dispatchEvent(new dom.window.Event('input',{bubbles:true}));});}
async function filtrar(v){const e=document.querySelector('.record-explorer-filters select');await ejecutar(()=>{e.value=v;e.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});}
const tabla=()=>document.querySelector('.record-explorer > div:not(.record-explorer-filters) table');
const panel=()=>document.querySelector('.record-explorer-detail');
(async()=>{
 const root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(h(DetalleProductos,{elementos})));
 assert.equal(document.querySelectorAll('details').length,0);assert.equal(tabla().querySelectorAll('tbody tr').length,10);
 assert.ok(document.body.textContent.includes('139 de 139 productos'));
 await click('Última página');assert.equal(tabla().querySelectorAll('tbody tr').length,9);
 await click('Ver detalle de Producto 139');assert.ok(panel().textContent.includes('Pronóstico #938'));
 await buscar('PRO-1');assert.equal(panel().hidden,true);assert.ok(tabla().textContent.includes('12 MACARON'));
 await buscar('azucar');assert.equal(tabla().querySelectorAll('tbody tr').length,1);
 await click('Ver detalle de Azúcar especial');assert.equal(document.activeElement,panel());
 assert.equal([...tabla().querySelectorAll('td')].filter(x=>x.textContent==='No disponible').length,3);
 assert.ok(panel().textContent.includes('No hay una receta disponible'));
 await click('Lotes consultados (0)',panel());assert.ok(panel().textContent.includes('No había lotes registrados'));
 await click('Limpiar búsqueda y filtros');await filtrar('stock');assert.equal(tabla().querySelectorAll('tbody tr').length,1);
 await filtrar('avisos');assert.equal(tabla().querySelectorAll('tbody tr').length,1);
 await filtrar('producir');assert.ok(document.body.textContent.includes('138 de 139'));
 await click('Limpiar búsqueda y filtros');await click('Ver detalle de 12 MACARON');
 assert.ok(panel().textContent.includes('Receta #31, versión 3')&&panel().textContent.includes('250 g'));
 await click('Lotes consultados (2)',panel());
 for(const t of ['VIGENTE','VENCIDO','Incluido','Excluido','2026-11-05','Desconocida','Desconocido'])assert.ok(panel().textContent.includes(t),t);
 await click('Cerrar detalle del producto');assert.equal(document.activeElement,boton('Ver detalle de 12 MACARON'));
 await click('Ver detalle de 12 MACARON');await click('Ver detalle de Producto 3');
 assert.equal(document.querySelectorAll('.record-explorer-detail:not([hidden])').length,1);
 assert.equal(boton('Receta conservada (1)',panel()).getAttribute('aria-pressed'),'true','Cambiar producto reinicia la vista');
 await buscar('inexistente');assert.ok(document.body.textContent.includes('No hay productos con esos filtros'));assert.equal(panel().hidden,true);
 await ejecutar(()=>root.render(h(DetalleLineasVenta,{lineas})));
 assert.equal(tabla().querySelectorAll('tbody tr').length,10);assert.equal(document.querySelectorAll('details').length,0);
 await click('Ver detalle de 12 MACARON');assert.ok(tabla().textContent.includes('3.33'),'No recalcular subtotal a partir del precio base');
 assert.ok(panel().textContent.includes('#950'));assert.equal(panel().querySelectorAll('tbody tr').length,10);
 await click('Siguiente',panel());assert.equal(panel().querySelectorAll('tbody tr').length,2);assert.ok(panel().textContent.includes('#111'));
 await buscar('PRO-139');assert.equal(tabla().querySelectorAll('tbody tr').length,1);assert.equal(panel().hidden,true);
 await ejecutar(()=>root.render(h(ExploradorDetalle,{filas:elementos,idFila:e=>e.producto_id,nombre:e=>e.stock.nombre,textoBusqueda:e=>`${e.stock.nombre} ${e.stock.codigo}`,etiquetaBusqueda:'Buscar producto seleccionado'})));
 assert.equal(document.querySelector('.record-explorer-detail'),null);assert.equal(tabla().querySelectorAll('tbody tr').length,10);
 await buscar('azucar');assert.equal(tabla().querySelectorAll('tbody tr').length,1);
 assert.equal(JSON.stringify({elementos,lineas}),original);
 await ejecutar(()=>root.unmount());
 console.log('OK trazas: 139 productos, búsqueda/paginación/filtros, panel único y foco, receta/lotes conservados, null, movimientos/compensaciones, subtotal canónico y resumen de solo lectura. Sin red.');
})().catch(e=>{console.error(e);process.exitCode=1;});
