// Regresión React del backport: respuesta perdida, remontaje y caja única. Sin red.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const {JSDOM}=req('jsdom'),dom=new JSDOM('<div id="root"></div>',{url:'http://operaciones.test/'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,sessionStorage:dom.window.sessionStorage,IS_REACT_ACT_ENVIRONMENT:true});
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
const ts=req('typescript');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const resolver=Module._resolveFilename,originalLoad=Module._load;
Module._resolveFilename=function(n,...args){return resolver.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...args);};
const React=req('react'),{act}=React,{createRoot}=req('react-dom/client');
const contexto={token:'fixture',perfil:{id:1,rol:'ADMINISTRADOR'},negocio:{zona_horaria:'America/Lima'}};
Module._load=function(n,...args){
 if(n==='@/components/layout/ProtectedShell')return {ProtectedShell:({children})=>children(contexto)};
 if(n==='next/link')return {__esModule:true,default:({children,...props})=>React.createElement('a',props,children)};
 return originalLoad.call(this,n,...args);
};
const Pagina=require('../frontend/src/app/operaciones/page.tsx').default;
let posts=[],perderRespuesta=true,registros=new Map(),cantidad=0;
global.fetch=async(url,opt={})=>{
 const ruta=new URL(url).pathname.replace('/api/v1','');let datos;
 if(ruta==='/operaciones/resumen')datos={fecha_operativa:'2026-10-28',productos:[{id:1,nombre:'Pan QA',codigo:'PAN'}],
  planes:[{id:1,fecha:'2026-10-28',lineas:[{producto_id:1,nombre:'Pan QA',previsto:6,producido:cantidad,pendiente:6-cantidad}]}],
  configuracion:{reloj:'ACTUAL',fecha_escenario:null,hora_escenario:'17:15',producto_ids:[],habilitada:false},pedidos:[],promociones:[],registros:[]};
 else if(ruta==='/operaciones/producciones'){
  const b=JSON.parse(opt.body);posts.push(b);
  if(!registros.has(b.clave_idempotencia)){cantidad+=b.lineas[0].cantidad;registros.set(b.clave_idempotencia,{id:registros.size+1});}
  datos=registros.get(b.clave_idempotencia);
  if(perderRespuesta){perderRespuesta=false;throw new TypeError('Respuesta perdida de prueba');}
 }else throw Error('Solicitud inesperada '+ruta);
 return {ok:true,status:200,text:async()=>JSON.stringify({datos})};
};
const pausa=()=>new Promise(r=>setTimeout(r,0));
async function ejecutar(f){await act(async()=>{f?.();await pausa();await pausa();});}
function boton(t){const b=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===t);assert.ok(b,'Falta '+t);return b;}
async function seleccionar(n,v){await ejecutar(()=>{const s=document.querySelectorAll('select')[n];s.value=v;s.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});}
async function enviar(){await ejecutar(()=>document.querySelector('form').dispatchEvent(new dom.window.Event('submit',{bubbles:true,cancelable:true})));}
(async()=>{
 let root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(Pagina)));
 assert.ok(document.querySelector('a[href="/ventas"]'),'Debe enlazar nuestra caja');
 assert.ok(![...document.querySelectorAll('button')].some(b=>['Ventas','Tienda'].includes(b.textContent.trim())),'No duplicar caja/tienda');
 await seleccionar(0,'1');await seleccionar(1,'1');await enviar();
 assert.equal(posts.length,1);assert.equal(cantidad,1);
 assert.ok(document.querySelector('fieldset').disabled,'Bloquear cambios tras respuesta incierta');
 assert.ok(sessionStorage.getItem('foodsave-operacion-pendiente:1'));
 await ejecutar(()=>root.unmount());
 root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(Pagina)));
 await ejecutar(()=>boton('Recuperar operación pendiente').click());
 assert.equal(posts.length,2);assert.deepEqual(posts[0],posts[1]);assert.equal(cantidad,1);
 assert.equal(sessionStorage.getItem('foodsave-operacion-pendiente:1'),null);
 assert.equal(document.querySelector('select').value,'','Formulario nuevo después de recuperar');
 await seleccionar(0,'1');await seleccionar(1,'1');await enviar();
 assert.equal(cantidad,2);assert.notEqual(posts[2].clave_idempotencia,posts[0].clave_idempotencia);
 await ejecutar(()=>root.unmount());
 console.log('OK operaciones React: caja única, tienda separada, respuesta perdida, remontaje y recuperación con misma clave sin duplicar producción. API falsa, sin red.');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>dom.window.close());
