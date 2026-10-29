/* Componente real con React/jsdom, API falsa y sin datos del comercio. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module');
const raiz=path.resolve(__dirname,'..'),req=Module.createRequire(path.join(raiz,'frontend/package.json'));
const {JSDOM}=req('jsdom'),dom=new JSDOM('<!doctype html><html><body><div id="root"></div></body></html>',{url:'http://entradas.test/'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,sessionStorage:dom.window.sessionStorage,IS_REACT_ACT_ENVIRONMENT:true});
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
dom.window.HTMLDialogElement.prototype.showModal=function(){this.open=true;};
dom.window.HTMLDialogElement.prototype.close=function(){this.open=false;};
const ts=req('typescript');
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:f}).outputText,f);
const resolver=Module._resolveFilename;
Module._resolveFilename=function(n,...args){return resolver.call(this,n.startsWith('@/')?path.join(raiz,'frontend/src',n.slice(2)):n,...args);};
const React=req('react'),{act}=React,{createRoot}=req('react-dom/client');
const {EntradasProductos}=require('../frontend/src/features/inventario/EntradasProductos.tsx');
let entrada=null,posts=[],perderRespuesta=false,cambios=[];
const contexto={token:'fixture',perfil:{id:1,rol:'ADMINISTRADOR',nombre:'QA'},negocio:{zona_horaria:'America/Lima'}};
const productos=[{id:1,codigo:'PAN',nombre:'Pan QA',activo:true},{id:2,codigo:'CRO',nombre:'Croissant QA',activo:true}];
function guardar(b){return {id:1,numero:'E-00000001',fecha_entrada:b.fecha_entrada,motivo:b.motivo,usuario_id:1,nombre_usuario:'QA',creado_en:'2026-10-28T15:00:00Z',lineas:b.lineas.map((l,i)=>({...l,id:i+1,lote_id:i+1,movimiento_id:i+1,nombre_producto:productos.find(p=>p.id===l.producto_id).nombre,codigo_producto:productos.find(p=>p.id===l.producto_id).codigo}))};}
global.fetch=async(url,opt={})=>{
 const ruta=new URL(url).pathname.replace('/api/v1',''),metodo=opt.method??'GET';let datos,status=200,metadatos;
 if(ruta.endsWith('/contexto'))datos={fecha_actual:'2026-10-28',zona_horaria:'America/Lima',vida_maxima_dias:5,productos};
 else if(ruta.includes('/por-clave/')){datos=entrada;status=entrada?200:404;}
 else if(ruta==='/inventario/entradas-productos'&&metodo==='GET'){datos=entrada?[entrada]:[];metadatos={total:datos.length};}
 else if(ruta==='/inventario/entradas-productos'&&metodo==='POST'){
  const body=JSON.parse(opt.body);posts.push(body);entrada??=guardar(body);datos=entrada;status=201;
  if(perderRespuesta){perderRespuesta=false;throw new TypeError('Respuesta perdida de prueba');}
 }else throw Error(`Solicitud inesperada ${metodo} ${ruta}`);
 return {ok:status<400,status,text:async()=>JSON.stringify(status===404?{error:{codigo:'ENTRADA_NO_ENCONTRADA',mensaje:'Sin resultado'}}:{datos,metadatos})};
};
const actualizar=(...args)=>cambios.push(args),pausa=()=>new Promise(r=>setTimeout(r,0));
async function ejecutar(f){await act(async()=>{f?.();await pausa();await pausa();});}
function boton(t){const b=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===t);assert.ok(b,`Falta botón ${t}`);return b;}
const click=t=>ejecutar(()=>boton(t).click());
async function escribir(campo,valor,grupo=document){
 const label=[...grupo.querySelectorAll('label')].find(l=>l.textContent.trim()===campo);assert.ok(label,`Falta campo ${campo}`);
 const e=label.querySelector('input'),set=Object.getOwnPropertyDescriptor(dom.window.HTMLInputElement.prototype,'value').set;
 await ejecutar(()=>{set.call(e,valor);e.dispatchEvent(new dom.window.Event('input',{bubbles:true}));});
}
async function preparar(){
 await click('Registrar entrada');
 assert.equal(document.querySelector('dialog').open,true);
 await escribir('Motivo','Entrada de dos productos');
 const seleccionar=async(n,id)=>ejecutar(()=>{const s=document.querySelectorAll('fieldset')[n].querySelector('select');s.value=String(id);s.dispatchEvent(new dom.window.Event('change',{bubbles:true}));});
 await seleccionar(0,1);await escribir('Cantidad (unidades)','10',document.querySelectorAll('fieldset')[0]);
 await click('Agregar otro lote');await seleccionar(1,2);await escribir('Cantidad (unidades)','5',document.querySelectorAll('fieldset')[1]);
 assert.equal(document.querySelectorAll('fieldset').length,2);
 await ejecutar(()=>document.querySelector('dialog form').dispatchEvent(new dom.window.Event('submit',{bubbles:true,cancelable:true})));
 assert.ok(document.querySelector('dialog').textContent.includes('Revisa tu entrada'));
}
(async()=>{
 let root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(EntradasProductos,{contexto,onActualizar:actualizar})));
 assert.deepEqual(cambios[0],['2026-10-28',false],'Debe consultar hoy al iniciar');
 await preparar();await ejecutar(()=>{boton('Confirmar entrada').click();boton('Confirmar entrada').click();});
 assert.equal(posts.length,1,'Doble clic no debe duplicar la entrada');
 assert.deepEqual(posts[0].lineas.map(l=>[l.producto_id,l.cantidad]),[[1,10],[2,5]]);
 assert.ok(cambios.some(([f,p])=>f==='2026-10-28'&&p===true),'Debe actualizar el stock de productos al confirmar');
 assert.equal(sessionStorage.getItem('foodsave:entrada:pendiente:1'),null);
 await ejecutar(()=>root.unmount());
 entrada=null;posts=[];perderRespuesta=true;
 root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(EntradasProductos,{contexto,onActualizar:actualizar})));
 await preparar();await click('Confirmar entrada');
 assert.equal(posts.length,1);assert.equal(JSON.parse(sessionStorage.getItem('foodsave:entrada:pendiente:1')).clave_operacion,posts[0].clave_operacion);
 await ejecutar(()=>root.unmount());
 root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(EntradasProductos,{contexto,onActualizar:actualizar})));
 assert.ok(document.body.textContent.includes('recuperada'));assert.equal(posts.length,1,'Recuperar no debe repetir POST');
 assert.equal(sessionStorage.getItem('foodsave:entrada:pendiente:1'),null);
 await ejecutar(()=>root.unmount());
 root=createRoot(document.getElementById('root'));
 await ejecutar(()=>root.render(React.createElement(EntradasProductos,{contexto:{...contexto,perfil:{...contexto.perfil,id:2,rol:'OPERADOR'}},onActualizar:actualizar})));
 assert.ok(![...document.querySelectorAll('button')].some(b=>b.textContent.trim()==='Registrar entrada'),'Operador solo consulta');
 await ejecutar(()=>root.unmount());
 console.log('OK entradas React: varios lotes, revisión, cantidades, fecha actual, doble clic, recuperación sin duplicación y permisos. API falsa, sin red.');
})().catch(e=>{console.error(e);process.exitCode=1;});
