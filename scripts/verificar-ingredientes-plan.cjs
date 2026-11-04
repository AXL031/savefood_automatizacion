/* Explorador real de ingredientes con React/jsdom; snapshots ficticios, sin red. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const {JSDOM}=req('jsdom'),dom=new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>',{url:'http://planes.test/'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,IS_REACT_ACT_ENVIRONMENT:true});
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
dom.window.HTMLElement.prototype.scrollIntoView=function(){};
global.fetch=()=>{throw new Error('No se debe consultar una API al explorar el snapshot');};
const ts=req('typescript');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const resolver=Module._resolveFilename;
Module._resolveFilename=function(n,...a){return resolver.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...a);};
const React=req('react'),{act}=React,{createRoot}=req('react-dom/client'),{DetalleIngredientes}=require('../frontend/src/features/planificacion/DetalleIngredientes.tsx');
const h=React.createElement;
const stock=(id,nombre)=>({tipo:'ingrediente',item_id:id,codigo:'ING-'+id,nombre,unidad:'g',stock_conocido:true,cantidad_disponible:'2000.000',cantidad_prioridad:'0',cantidad_excluida:'0',vigencia_desconocida:false,lotes:[]});
const necesidades=[
 {ingrediente_id:1,unidad_base:'g',cantidad_necesaria:'3000.000',stock_disponible:'2000.000',faltante:'1000.000',estado:'CALCULADO',stock:{...stock(1,'Harina de trigo'),lotes:[{lote_id:1,codigo_lote:'HAR-VIGENTE',saldo:'2000.000',cuenta:true,motivo:'VIGENTE',fecha_caducidad:'2026-11-06'},{lote_id:2,codigo_lote:'HAR-VENCIDO',saldo:'400.000',cuenta:false,motivo:'VENCIDO',fecha_caducidad:'2026-10-30'}]},aportes:[{producto_id:7,receta_id:12,version_receta:3,cantidad_producir:10,cantidad_por_unidad:'300.000',aporte:'3000.000'}]},
 {ingrediente_id:2,unidad_base:'g',cantidad_necesaria:'150.000',stock_disponible:null,faltante:null,estado:'STOCK_DESCONOCIDO',stock:{...stock(2,'Agua'),stock_conocido:false,cantidad_disponible:null},aportes:[]},
 {ingrediente_id:3,unidad_base:'g',cantidad_necesaria:'200.000',stock_disponible:'500.000',faltante:'0.000',estado:'CALCULADO',stock:stock(3,'Azúcar'),aportes:[]},
];
const elementos=[{producto_id:7,stock:{nombre:'Baguette'}}],original=JSON.stringify(necesidades);
const pausa=()=>new Promise(r=>setTimeout(r,0));
async function ejecutar(fn){await act(async()=>{fn?.();await pausa();});}
function boton(texto){const b=[...document.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')===texto||b.textContent===texto);assert.ok(b,'Falta botón '+texto);return b;}
async function click(t){await ejecutar(()=>boton(t).click());}
async function buscar(valor){const el=document.querySelector('input[type="search"]');await ejecutar(()=>{Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype,'value').set.call(el,valor);el.dispatchEvent(new dom.window.Event('input',{bubbles:true}));});}
async function filtrar(valor){const el=document.querySelector('.plan-ingredients-filters select');await ejecutar(()=>{el.value=valor;el.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});}
(async()=>{
 const root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(h(DetalleIngredientes,{necesidades,elementos})));
 assert.equal(document.querySelectorAll('details').length,0,'No repetir desplegables por ingrediente');
 assert.equal(document.querySelectorAll('section.plan-ingredient-detail:not([hidden])').length,0);
 await click('Ver detalle de Harina de trigo');
 const panel=()=>document.querySelector('.plan-ingredient-detail');
 assert.equal(panel().hidden,false);assert.equal(document.activeElement,panel());
 assert.ok(panel().textContent.includes('Baguette')&&panel().textContent.includes('Receta #12 · versión 3'));
 assert.ok(panel().textContent.includes('3 kg')&&panel().textContent.includes('300 g'));
 await click('Lotes consultados (2)');
 assert.ok(panel().textContent.includes('HAR-VIGENTE')&&panel().textContent.includes('HAR-VENCIDO'));
 assert.ok(panel().textContent.includes('Incluido')&&panel().textContent.includes('Excluido'));
 await click('Cerrar detalle del ingrediente');
 assert.equal(panel().hidden,true);assert.equal(document.activeElement,boton('Ver detalle de Harina de trigo'));
 await filtrar('sin-stock');
 assert.equal(document.querySelectorAll('.plan-ingredients > .plan-ingredients-table tbody tr').length,1);
 await click('Ver detalle de Agua');
 assert.equal(panel().querySelectorAll('dd').length,3);
 assert.equal([...panel().querySelectorAll('dd')].filter(e=>e.textContent==='No disponible').length,2,'null no se convierte en cero');
 assert.ok(panel().textContent.includes('no tiene aportes calculables'));
 await click('Lotes consultados (0)');assert.ok(panel().textContent.includes('No había lotes registrados'));
 await click('Limpiar filtros');await buscar('azucar');
 assert.equal(document.querySelectorAll('.plan-ingredients > .plan-ingredients-table tbody tr').length,1);
 assert.ok(document.querySelector('.plan-ingredients > .plan-ingredients-table').textContent.includes('Azúcar'));
 await buscar('inexistente');assert.ok(document.body.textContent.includes('No hay ingredientes con esos filtros'));
 await click('Limpiar filtros');await filtrar('faltantes');
 assert.equal(document.querySelectorAll('.plan-ingredients > .plan-ingredients-table tbody tr').length,1);
 assert.equal(JSON.stringify(necesidades),original,'No mutar snapshots');
 await ejecutar(()=>root.unmount());
 console.log('OK ingredientes del plan: búsqueda sin tildes, filtros, detalle único, foco, aportes/recetas, lotes incluidos/excluidos, null conservado y cero red.');
})().catch(e=>{console.error(e);process.exitCode=1;});
