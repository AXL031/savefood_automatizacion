// Componente real con reloj fijo, sin red ni tareas reales.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const {JSDOM}=req('jsdom'),dom=new JSDOM('<div id="root"></div>',{url:'http://promociones.test/'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,IS_REACT_ACT_ENVIRONMENT:true});
dom.window.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
dom.window.HTMLDialogElement.prototype.close=function(){this.open=false;};
const ts=req('typescript');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const resolver=Module._resolveFilename,originalLoad=Module._load;
Module._resolveFilename=function(n,...a){return resolver.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...a);};
const React=req('react'),{act}=React,{createRoot}=req('react-dom/client');
Module._load=function(n,...a){if(n==='next/link')return {__esModule:true,default:({children,...p})=>React.createElement('a',p,children)};return originalLoad.call(this,n,...a);};
global.fetch=()=>{throw Error('Red prohibida en esta comprobación');};
const {PromocionesOperacion,enDosMinutos}=require('../frontend/src/features/promociones/PromocionesOperacion.tsx');
const reloj=Date.now;Date.now=()=>Date.parse('2026-11-05T17:00:00Z');
assert.equal(enDosMinutos('America/Lima'),'2026-11-05T12:02:00');
const base={id:1,lote_id:10,producto:'Éclair QA',codigo_lote:'LOTE-QA',estado:'APROBADA',descuento:25,motivo:'Vence hoy',fecha:'2026-11-05',stock_disponible:8,fecha_limite_venta:'2026-11-05',activa_en_tienda:true,modo_publicacion:'AUTOMATICO',programacion:null};
const filas=[base,{...base,id:2,producto:'Otro pan',estado:'PENDIENTE',activa_en_tienda:false}];
let llamadas=[];
const root=createRoot(document.getElementById('root'));
const ejecutar=async(...args)=>{llamadas.push(args);return true;};
async function paso(f){await act(async()=>{await f();await new Promise(r=>setTimeout(r,0));});}
const boton=t=>{const b=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===t);assert.ok(b,'Falta botón '+t);return b;};
function valor(selector,v){const e=document.querySelector(selector);const proto=e.tagName==='SELECT'?dom.window.HTMLSelectElement.prototype:dom.window.HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(e,v);e.dispatchEvent(new dom.window.Event(e.tagName==='SELECT'?'change':'input',{bubbles:true}));}
(async()=>{
 await paso(()=>root.render(React.createElement(PromocionesOperacion,{filas,ejecutar,zona:'America/Lima',modoPredeterminado:'AUTOMATICO',ocupado:false,bloqueado:false,error:''})));
 await paso(()=>valor('select','ACTIVAS'));assert.equal(document.querySelectorAll('tbody tr').length,1);
 await paso(()=>valor('input[type=search]','eclair'));assert.equal(document.querySelectorAll('tbody tr').length,1);
 await paso(()=>boton('Programar publicación').click());
 assert.ok(document.querySelector('dialog').textContent.includes('dejará de estar visible'));
 assert.equal(document.querySelector('input[type=datetime-local]').value,'2026-11-05T12:02');
 await paso(()=>document.querySelector('dialog form').dispatchEvent(new dom.window.Event('submit',{bubbles:true,cancelable:true})));
 assert.equal(llamadas.length,1);assert.equal(llamadas[0][0],'/operaciones/promociones/1/programar');
 assert.equal(llamadas[0][1].modo_publicacion,'AUTOMATICO');assert.ok(llamadas[0][1].fecha_hora_local.startsWith('2026-11-05T12:02'));assert.ok(llamadas[0][1].clave_idempotencia);
 assert.equal(document.querySelector('dialog'),null);
 await paso(()=>root.unmount());Date.now=reloj;
 console.log('OK promociones: filtro activo, búsqueda sin tildes, hora +2 minutos en zona del negocio, retirada advertida y solicitud idempotente sin red.');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{Date.now=reloj;});
